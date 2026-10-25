"""Research preview: OpenAI compatible agent operating only the Billing Config test site."""
import argparse, csv, json, os, re, time, uuid
from pathlib import Path
from urllib.parse import urlparse
from openai import OpenAI
from playwright.sync_api import sync_playwright

URL = "https://shiningcao77.github.io/Billing_Config/"
SYSTEM = """You simulate a participant in a usability task. Consider the supplied research
profile as context, not mandatory behaviors. Use only the task and currently visible UI.
Never invent unseen page content or reproduce human test observations.
Select exactly one action per turn from the listed visible controls.
Briefly verbalize what you think at meaningful points without disclosing hidden reasoning.
Return only JSON: {"action":"click|fill|select|check|uncheck|back|finish|stop",
"target":"numeric control index or empty","value":"text or empty","think_aloud":"brief statement"}.
If unable to proceed choose stop. If finished choose finish. No credentials."""

def permitted(url):
    x = urlparse(url)
    return x.scheme == "https" and x.hostname == "shiningcao77.github.io" and x.path.startswith("/Billing_Config/")

def observe(page):
    elements = page.evaluate("""() => {
      const tags='button,a[href],input:not([type="hidden"]),select,textarea,[role="button"],[role="checkbox"],[role="radio"],[tabindex="0"]';
      return [...document.querySelectorAll(tags)].filter(e=>{
        const r=e.getBoundingClientRect(),s=getComputedStyle(e);
        return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'
      }).slice(0,100).map((e,i)=>{
        e.setAttribute('data-personalab-index',String(i));
        return {index:i,tag:e.tagName.toLowerCase(),
          role:e.getAttribute('role')||e.tagName.toLowerCase(),
          label:String(e.getAttribute('aria-label')||e.innerText||e.getAttribute('placeholder')||e.value||'').replace(/\\s+/g,' ').trim().slice(0,130),
          type:e.getAttribute('type'),value:e.value||'',checked:!!e.checked,
          options:e.tagName==='SELECT'?[...e.options].map(o=>({text:o.text,value:o.value})).slice(0,35):undefined};
      })
    }""")
    return {"url":page.url,"title":page.title(),
            "visible_text":page.locator("body").inner_text(timeout=10000)[:8000],
            "elements":elements}

def choose(client,model,profile,task,obs,history):
    reply=client.chat.completions.create(
        model=model,temperature=0.5,
        messages=[{"role":"system","content":SYSTEM},
                  {"role":"user","content":json.dumps({"profile":profile,"task":task,
                    "observation":obs,"recent_actions":history[-8:]},ensure_ascii=False)}])
    raw=(reply.choices[0].message.content or "").strip()
    raw=re.sub(r'^\\x60{3}(?:json)?\\s*|\\s*\\x60{3}$','',raw)
    try: return json.loads(raw)
    except json.JSONDecodeError:
        match=re.search(r'\\{[\\s\\S]*\\}',raw)
        if not match: raise
        return json.loads(match.group(0))

def perform(page,choice,obs):
    action=choice.get("action")
    if action in ("finish","stop"): return action
    if action=="back":
        page.go_back(wait_until="domcontentloaded",timeout=12000)
        return "executed"
    try: idx=int(choice.get("target"))
    except (ValueError,TypeError): raise ValueError("Invalid target index")
    if idx not in [x["index"] for x in obs["elements"]]:
        raise ValueError("Target not visible in current observation")
    element=page.locator('[data-personalab-index="'+str(idx)+'"]').first
    if action=="click": element.click(timeout=6000)
    elif action=="fill": element.fill(str(choice.get("value","")),timeout=6000)
    elif action=="select":
        value=str(choice.get("value",""))
        try: element.select_option(label=value,timeout=5000)
        except Exception: element.select_option(value=value,timeout=5000)
    elif action=="check": element.check(timeout=6000)
    elif action=="uncheck": element.uncheck(timeout=6000)
    else: raise ValueError("Unsupported action")
    return "executed"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--profile",default="participant004.json")
    parser.add_argument("--task",default="task.txt")
    parser.add_argument("--model",default=os.getenv("OPENAI_MODEL","gpt-4o-mini"))
    parser.add_argument("--runs",type=int,default=1)
    parser.add_argument("--steps",type=int,default=45)
    parser.add_argument("--headed",action="store_true")
    args=parser.parse_args()
    if not os.getenv("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY in your environment, never in the repository.")
    if args.runs<1 or args.steps<1: parser.error("Positive runs and steps required")
    base=os.getenv("OPENAI_BASE_URL")
    client=OpenAI(api_key=os.environ["OPENAI_API_KEY"],**({"base_url":base} if base else {}))
    profile=json.loads(Path(args.profile).read_text())
    task=Path(args.task).read_text()
    output=Path("browser_results"); output.mkdir(exist_ok=True)
    summary=[]
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=not args.headed)
        try:
            for _ in range(args.runs):
                ctx=browser.new_context(accept_downloads=False,viewport={"width":1360,"height":850})
                page=ctx.new_page()
                rid=str(profile.get("participant_code","participant"))+"_"+uuid.uuid4().hex[:8]
                events=[];history=[];start=time.monotonic();status="step_limit"
                try:
                    page.goto(URL,wait_until="domcontentloaded",timeout=30000)
                    for seq in range(args.steps):
                        if not permitted(page.url):
                            status="out_of_scope_navigation"; break
                        obs=observe(page)
                        choice=choose(client,args.model,profile,task,obs,history)
                        event={"seq":seq+1,"elapsed_ms":round((time.monotonic()-start)*1000),
                               "page":obs["url"],"action":choice.get("action"),
                               "target":choice.get("target"),"value":choice.get("value"),
                               "think_aloud":choice.get("think_aloud"),"status":"pending"}
                        try:
                            event["status"]=perform(page,choice,obs)
                            if event["status"] in ("finish","stop"):
                                status=event["status"];events.append(event);break
                            page.wait_for_timeout(350)
                            if not permitted(page.url):
                                status="out_of_scope_navigation";events.append(event);break
                        except Exception as e:
                            event["status"]="action_error";event["error"]=str(e)[:400]
                        events.append(event)
                        history.append({k:event.get(k) for k in ("action","target","value","status")})
                except Exception as e:
                    status="runtime_error"
                    events.append({"status":status,"error":str(e)[:800]})
                finally:
                    try: page.screenshot(path=str(output/(rid+".png")),full_page=True,timeout=6000)
                    except Exception: pass
                    try:
                        saved=page.evaluate("""() => Object.fromEntries(Object.keys(localStorage).filter(k=>/budget/i.test(k)).map(k=>[k,(localStorage.getItem(k)||'').slice(0,5000)]))""")
                    except Exception: saved={}
                    (output/(rid+".json")).write_text(json.dumps({"run_id":rid,"model":args.model,
                        "status":status,"events":events,"local_budget_state":saved,
                        "note":"Completion declarations do not prove task success; grade separately."},indent=2))
                    summary.append({"run_id":rid,"status":status,"actions":len(events)})
                    ctx.close()
        finally: browser.close()
    with (output/"summary.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["run_id","status","actions"]);writer.writeheader();writer.writerows(summary)
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()

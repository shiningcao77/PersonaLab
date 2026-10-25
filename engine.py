import json, random, argparse, csv
from pathlib import Path

STEPS = ['find_billing','open_budgets','create_budget','set_scope','set_amount','set_alerts','review','save','confirm']

def clamp(x): return max(0.0,min(1.0,x))
def simulate(profile, seed):
    r=random.Random(seed)
    traits=profile['traits']
    accuracy=(traits['accuracy']-1)/4
    persistence=(traits['persistence']-1)/4
    caution=(traits['caution']-1)/4
    attention=(traits['attention']-1)/4
    knowledge=profile.get('billing_knowledge','limited')
    familiarity={'none':0.0,'limited':0.25,'moderate':0.6,'extensive':0.9}[knowledge]
    events=[]; errors=[]; actions=0; abandoned=False; values={'scope':'all_projects','amount':None,'threshold':50,'actual':True,'owners':False,'admins':True}
    def event(step,kind,detail):
        nonlocal actions
        actions+=1; events.append({'seq':actions,'step':step,'event':kind,'detail':detail})
    for step in STEPS:
        event(step,'step_entered',step)
        if step in ('find_billing','open_budgets'):
            if r.random()<clamp(.48-.28*familiarity-.14*attention):
                event(step,'wrong_turn','navigation uncertainty'); errors.append('navigation')
                if r.random()<clamp(.35-.28*persistence): abandoned=True; break
            event(step,'navigate','target reached')
        elif step=='create_budget': event(step,'click','create budget')
        elif step=='set_scope':
            if r.random()<clamp(.45+.30*attention+.15*familiarity): values['scope']='Atlas'
            else: errors.append('scope_default')
            event(step,'field_changed',{'scope':values['scope']})
        elif step=='set_amount':
            values['amount']=800 if r.random()<clamp(.50+.25*familiarity+.10*attention) else 1000
            event(step,'field_changed',{'amount':values['amount']})
        elif step=='set_alerts':
            if r.random()<clamp(.45+.25*attention+.15*accuracy): values['owners']=True
            if r.random()<clamp(.25+.35*attention+.20*caution): values['admins']=False
            if values['amount']==1000 and r.random()<clamp(.25+.35*familiarity+.15*accuracy): values['threshold']=80
            if values['amount']==800 and r.random()<clamp(.25+.25*attention): values['threshold']=100
            event(step,'field_changed',{'threshold':values['threshold'],'owners':values['owners'],'admins':values['admins']})
        elif step=='review':
            if r.random()<clamp(.15+.45*accuracy+.20*caution):
                event(step,'review','inspect settings')
                if values['scope']!='Atlas' and r.random()<.6: values['scope']='Atlas';event(step,'correction','scope')
                if not values['owners'] and r.random()<.6: values['owners']=True;event(step,'correction','owners')
                if values['admins'] and r.random()<.5: values['admins']=False;event(step,'correction','admins')
        elif step=='save': event(step,'save_succeeded',dict(values))
        elif step=='confirm':
            if r.random()<clamp(.3+.3*caution+.2*accuracy): event(step,'confirmation_checked','budget list')
    correct=(values['scope']=='Atlas' and values['owners'] and not values['admins'] and values['actual'] and ((values['amount']==800 and values['threshold']==100) or (values['amount']==1000 and values['threshold']==80)))
    return {'participant_id':profile['participant_id'],'seed':seed,'completed':not abandoned,'correct':bool(correct and not abandoned),'actions':actions,'errors':errors,'saved':values if not abandoned else None,'events':events}

def main():
    p=argparse.ArgumentParser();p.add_argument('--profile',default='profile.json');p.add_argument('--runs',type=int,default=30);p.add_argument('--seed',type=int,default=100);p.add_argument('--output',default='results');a=p.parse_args()
    profile=json.loads(Path(a.profile).read_text()); out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    results=[simulate(profile,a.seed+i) for i in range(a.runs)]
    (out/'runs.json').write_text(json.dumps(results,indent=2))
    with (out/'summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['participant_id','seed','completed','correct','actions','errors']);w.writeheader()
        for x in results:w.writerow({k:json.dumps(x[k]) if k=='errors' else x[k] for k in w.fieldnames})
    print(json.dumps({'runs':len(results),'completion_rate':sum(x['completed'] for x in results)/len(results),'correct_rate':sum(x['correct'] for x in results)/len(results),'mean_actions':round(sum(x['actions'] for x in results)/len(results),2)},indent=2))
if __name__=='__main__':main()

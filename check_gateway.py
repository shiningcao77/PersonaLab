"""Test Cornell AI Gateway without exposing your API key."""
import os, sys
from openai import OpenAI

def main():
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("Missing OPENAI_API_KEY. Set it in your terminal; do not paste it into code.")
    base=os.getenv("OPENAI_BASE_URL","https://api.ai.it.cornell.edu")
    client=OpenAI(api_key=os.environ["OPENAI_API_KEY"],base_url=base,timeout=25)
    model=os.getenv("OPENAI_MODEL")
    if not model:
        try:
            models=client.models.list()
            names=[m.id for m in models.data]
            print("Gateway model IDs:", *names[:30],sep="\n  ")
            print("Set OPENAI_MODEL to an available chat model, then rerun.")
        except Exception as e:
            print("Model list unavailable. Check class documentation for the exact model ID.")
            print("Error type:",type(e).__name__)
        return
    try:
        response=client.chat.completions.create(
            model=model, messages=[{"role":"user","content":"Reply with the single word READY."}],
            max_tokens=24)
        print("Connection OK. Reply:",repr(response.choices[0].message.content))
    except Exception as e:
        print("Connection failed:",type(e).__name__,str(e)[:500])
        sys.exit(1)

if __name__=="__main__":main()

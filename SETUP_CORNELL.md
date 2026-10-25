# Cornell AI Gateway setup (Mac terminal)

The repo contains no API secrets. The Python OpenAI SDK uses the gateway URL `https://api.ai.it.cornell.edu` by default. The exact supported model ID and Chat Completions compatibility must be checked against your course's gateway documentation or with `check_gateway.py`.

## 1. Install

```bash
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
```

## 2. Set credentials in your terminal

```bash
export OPENAI_API_KEY='YOUR_NEW_CORNELL_KEY'
export OPENAI_BASE_URL='https://api.ai.it.cornell.edu'
```

Do not paste an API key in a GitHub file, ChatGPT message, or screenshot. If the original key was exposed, request rotation before using it again.

## 3. Find the model name / test API

```bash
python3 check_gateway.py
export OPENAI_MODEL='SUPPORTED_MODEL_ID'
python3 check_gateway.py
```

If `models.list()` is unavailable, get the supported model name from your course Notebook. If the gateway is not OpenAI Chat Completions compatible, the client will need a small adapter.

## 4. Try the agent

```bash
python3 browser_agent.py --model "$OPENAI_MODEL" --runs 1 --headed
```

The agent navigates the public Billing Config prototype; results and screenshot files are written to ignored `browser_results/`. Each run starts with a fresh browser context. The original offline `engine.py` stays unchanged.

**Limits:** This agent is an unvalidated research prototype. It has not been run with your course gateway credentials. A model saying it finished is not proof of correct saved settings. The script is configured only for the Billing Config website. Confirm that your course allows use for this practice and do not use a participant's private data without consent.

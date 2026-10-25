# PersonaLab Browser Agent

This is an experimental OpenAI compatible API and Playwright research browser agent. It does not modify the existing offline simulator in engine.py.

## Setup

Use Python 3.10 or newer.

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Set OPENAI_API_KEY as an environment variable. Set OPENAI_MODEL to the model your course API supports. Set OPENAI_BASE_URL only when your course uses a compatible custom endpoint. Never put your key in GitHub.

```bash
export OPENAI_API_KEY="your_key"
export OPENAI_MODEL="your_course_model"
# optional, if your course gateway requires it:
export OPENAI_BASE_URL="https://your_course_host/v1"
python browser_agent.py --model "$OPENAI_MODEL" --runs 1 --headed
```

Logs and screenshots are saved under browser_results. Isolated browser contexts reset site state for each run. The model chooses from visible browser elements rather than a predefined click sequence.

The agent has not been exercised against the live website or course API in this environment. The course gateway must support OpenAI compatible Chat Completions. Do not treat task completion declarations as verified correctness. Do not feed human task observations to the model. Keep the human task wording identical for a matched test. Model latency is included in event timestamps. Use a separate preregistered scoring rubric.

This script is restricted to the Billing Config host. Do not use credentials or run on unrelated sites. Confirm course API research permission and approved handling of participant profiles.
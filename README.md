# PersonaLab: Research Grounded Synthetic User Engine

An experimental, reproducible, research oriented behavioral simulator for the Atlas billing budget task.

## Run

Requires Python 3.9 or newer, with no external packages.

```bash
python engine.py --profile profile.json --runs 30 --seed 100 --output results
```

Outputs `results/runs.json` containing every simulated event, and `results/summary.csv` containing run outcomes.

## Input

The JSON profile accepts four independent research constructs on a 1 to 5 scale: accuracy, persistence, caution, attention. Billing knowledge is one of none, limited, moderate, extensive.

Do not populate input traits using observed target task behavior. Do not use human event traces to adjust the model before evaluating on those same traces.

## Limitations

This is a runnable **offline proof of concept**, not a browser automation agent or a validated digital twin. It simulates an abstract nine step billing workflow and does not click the live GitHub Pages prototype. The probabilities are explicit uncalibrated hypotheses, not learned coefficients. It models only a subset of the user's questionnaire. It does not model time, language, help seeking, or visual abilities. The demo profile is fictional, not a verified mapping of Participant 004. Grading uses the report's proposed acceptable $800 at 100 percent or $1000 at 80 percent solutions, with Atlas scope, actual spend, project owners, and no billing admins. These criteria should be confirmed with the research team before official use.

## Next engineering step

Replace abstract step transitions with Playwright browser observations and actions, instrument the prototype, and record actual DOM events and saved state. Freeze grading criteria and profile mapping before participant comparison.

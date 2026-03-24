# Agent Cold-start Smoke Test

This is the canonical first-run validation path for a newly arrived DrawForge agent.

Use it when you want to answer:

- can this machine reach the Visio bridge?
- can the repo preflight a job correctly?
- can the agent execute a known-good benchmark artifact chain?
- can the workflow export a preview and save a final `.vsdx`?

This test is intentionally narrower than "draw a brand-new figure from scratch."

## What this smoke test proves

It proves that the following chain is working:

`config -> workspace bootstrap -> bridge/token -> execute drawdsl -> export preview -> save final vsdx`

It does not prove that the repo can already analyze a brand-new image and produce high-quality `analysis.json`, `plan.json`, and `drawdsl.json` automatically.

## Prerequisites

- Microsoft Visio is reachable from the Windows environment
- the local bridge is running
- `VISIO_BRIDGE_TOKEN` is set in the shell you will use
- `InputReference/1.png` exists

If the bridge is not ready yet, see [WINDOWS_BRIDGE_DEPLOY.md](WINDOWS_BRIDGE_DEPLOY.md).

## Canonical files

- config:
  `Setup/examples/smoke-test-inputpng-1.json`
- preparation script:
  `Setup/prepare_smoke_test.py`
- source benchmark workspace:
  `Setup/jobs/inputpng-1/`

## Commands

From the repo root:

```powershell
python Setup\prepare_smoke_test.py --config Setup\examples\smoke-test-inputpng-1.json
python Setup\run_draw_job.py --config Setup\examples\smoke-test-inputpng-1.json
python Setup\execute_drawdsl.py --config Setup\examples\smoke-test-inputpng-1.json --round 1 --save-final
```

## Expected outputs

If the smoke test succeeds, you should see:

- preview:
  `OutputPreview/smoke-inputpng-1/round-01.png`
- final editable file:
  `OutputEditable/1_smoke_test_final.vsdx`
- runtime workspace:
  `.runtime/smoke-jobs/smoke-inputpng-1/`

## Why a runtime workspace is used

The smoke test should not mutate the tracked benchmark workspace under `Setup/jobs/inputpng-1/`.
Instead, the preparation script copies the benchmark artifacts into a disposable runtime workspace under `.runtime/`.

That gives a first-time agent a stable known-good benchmark while keeping the tracked repo state clean.

## Interpreting results

If `prepare_smoke_test.py` fails:

- the benchmark workspace or input file is missing

If `run_draw_job.py` fails:

- the config, bridge, token, or Visio reachability is broken

If `execute_drawdsl.py` fails:

- the execution layer or runtime environment is not healthy enough yet

If all three succeed:

- the environment is ready for controlled benchmark runs
- the next step is either real job work or deeper repo improvement

## Recommended next step for a new agent

After this smoke test passes:

1. inspect the produced preview
2. read the benchmark workspace artifacts
3. only then move on to a new image or structural repo improvements

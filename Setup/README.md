# Setup Workspace

`Setup/` is the entry point for one drawing job.

Its job is to answer:

- which figure are we drawing?
- where do outputs go?
- how many rounds are allowed?
- what gets saved or cleaned up?

It should not decide the diagram layout or directly operate Visio.

Useful entry docs:

- [../GET_STARTED.md](../GET_STARTED.md)
- [../MODE_POLICY.md](../MODE_POLICY.md)
- [../AGENT_START_HERE.md](../AGENT_START_HERE.md)
- [../docs/human/setup/AGENT_COLD_START_SMOKE_TEST.md](../docs/human/setup/AGENT_COLD_START_SMOKE_TEST.md)

## Files you edit manually

- `InputReference/<image>.png`
- `Setup/draw-job.local.json`

## Files the job workflow produces

- `Setup/jobs/<job>/run-summary.json`
- `Setup/jobs/<job>/analysis.json`
- `Setup/jobs/<job>/plan.json`
- `Setup/jobs/<job>/drawdsl.json`
- `Setup/jobs/<job>/reviews/`
- `OutputPreview/<job>/round-*.png`
- `OutputEditable/<final>.vsdx`

## Typical workflow

1. Put the reference PNG into `InputReference/`.
2. Copy `draw-job.template.json` to `draw-job.local.json`.
3. Edit the local config:

- `run_mode`
- `job_name`
- `task.input_png`
- `task.final_vsdx_name`
- `task.goal`
- `execution.max_rounds`

The config keys keep the current Visio-oriented names for compatibility:

- `task.input_png`
- `task.final_vsdx_name`

4. In the shell that can reach the Windows bridge, set:

- `VISIO_BRIDGE_TOKEN`
- optionally `VISIO_BRIDGE_BASE`

5. Run:

```powershell
python Setup\run_draw_job.py --config Setup\draw-job.local.json
```

This preflight will fail fast if:

- the input PNG is missing
- the bridge is down
- Visio cannot be reached
- the token is wrong

It also creates the standard job workspace.

## Canonical smoke test

For a fresh environment or a newly arrived agent, use the benchmark smoke test before open-ended job work:

```powershell
python Setup\prepare_smoke_test.py --config Setup\examples\smoke-test-inputpng-1.json
python Setup\run_draw_job.py --config Setup\examples\smoke-test-inputpng-1.json
python Setup\execute_drawdsl.py --config Setup\examples\smoke-test-inputpng-1.json --round 1 --save-final
```

This uses a disposable runtime workspace instead of mutating the tracked benchmark workspace.

## Development mode vs operation mode

`run_mode` can be:

- `development`
  - the agent may update repo structure or capabilities if the blocker is structural
- `operation`
  - the agent should mostly stay inside the current job workspace

Use `development` when you are still building the system itself.

## Final VSDX retention

- `execution.keep_final_vsdx: true`
  - save the final `.vsdx` into `OutputEditable/` on the last configured round
- `--save-final`
  - force saving the current round as the final `.vsdx`

## Important rule

Every round must leave evidence.

That means:

1. export a preview
2. write a round review
3. feed the important review findings back into the next round plan

When relevant, the round review should also capture:

- execution friction the agent hit
- missing capabilities or controls
- proposal candidates that seem structural but are not yet proven enough to become lessons

If a round is rerun without solving a prior issue or learning something new, it is not progress.

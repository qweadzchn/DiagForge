# Setup Workspace

`Setup/` is the entry point for one drawing job.

Its job is to answer:

- which figure are we drawing?
- where do outputs go?
- how many rounds are allowed?
- what gets saved or cleaned up?

It should not decide the diagram layout or directly operate Visio.

## Files you edit manually

- `InputPNG/<image>.png`
- `Setup/draw-job.local.json`

## Files the job workflow produces

- `Setup/jobs/<job>/run-summary.json`
- `Setup/jobs/<job>/analysis.json`
- `Setup/jobs/<job>/plan.json`
- `Setup/jobs/<job>/drawdsl.json`
- `Setup/jobs/<job>/reviews/`
- `OutputPreview/<job>/round-*.png`
- `OutputVSDX/<final>.vsdx`

## Typical workflow

1. Put the reference PNG into `InputPNG/`.
2. Copy `draw-job.template.json` to `draw-job.local.json`.
3. Edit the local config:

- `run_mode`
- `job_name`
- `task.input_png`
- `task.final_vsdx_name`
- `task.goal`
- `execution.max_rounds`

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

## Development mode vs operation mode

`run_mode` can be:

- `development`
  - the agent may update repo structure or capabilities if the blocker is structural
- `operation`
  - the agent should mostly stay inside the current job workspace

Use `development` when you are still building the system itself.

## Important rule

Every round must leave evidence.

That means:

1. export a preview
2. write a round review
3. feed the important review findings back into the next round plan

If a round is rerun without solving a prior issue or learning something new, it is not progress.

# Get Started

This file is the quickest human entry point for the repository.

## What You Need

- A Windows environment that can reach Microsoft Visio
- The Visio bridge running locally
- A bridge token available through `VISIO_BRIDGE_TOKEN`
- A reference image in `InputPNG/`

## Quick Path

1. Put the source image into `InputPNG/`.
2. Copy `Setup/draw-job.template.json` to `Setup/draw-job.local.json`.
3. Fill in the job name, input image, goal, and execution settings.
4. Start the bridge.
5. Run:

```powershell
python Setup\run_draw_job.py --config Setup\draw-job.local.json
```

## Where To Go Next

- Running a job: [Setup/README.md](Setup/README.md)
- Understanding the repository structure: [README.md](README.md)
- Agent onboarding: [AGENT_START_HERE.md](AGENT_START_HERE.md)
- Mode and write rules: [MODE_POLICY.md](MODE_POLICY.md)
- Operational docs: [docs/human/README.md](docs/human/README.md)

## Current Scope

The repository currently centers on Microsoft Visio as the execution backend.
It is still experimental, and many of the reusable assets are being refined while benchmark jobs are added and reviewed.

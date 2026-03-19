# DiagForge

让 agent 像人一样使用 Microsoft Visio 画图.

`DiagForge` is an agentic abstraction layer for diagram drawing on top of Microsoft Visio.
The goal is not "call a few Visio APIs".
The goal is to let an agent:

1. understand what the user wants to draw
2. choose how the figure should be laid out and styled
3. operate Visio reliably
4. look at its own result
5. review failures
6. turn repeated fixes into reusable assets

In this repo, the foundation model is the reasoning engine.
The durable asset is everything around it: the plans, drawing rules, Visio operations, review loop, and lessons.

## Why the name `DiagForge`

`Diag` points to the real object we care about:

- diagram logic
- spatial topology
- layout intent
- editable structure

`Forge` points to the working loop:

- take rough human intent and source material as input
- execute through software skills
- read back environment feedback
- reflect on failures
- revise the next round
- turn repeated fixes into durable assets

The point is not to freeze a PNG into dead pixels.
The point is to forge a live, structured, human-editable diagram asset on top of existing professional software.

## Why this repo exists

Most diagram automation projects stop at one of these points:

- they can generate a picture once, but cannot improve round by round
- they can operate software, but do not know how to draw well
- they can run a demo, but do not leave reusable planning and review artifacts

`DiagForge` is trying to build the missing middle layer:

- `intent -> plan -> drawdsl -> visio -> preview -> review -> lesson`

That is the core loop we want to keep even if the base model changes later.

## Layered architecture

The repo is split into five layers.
Each layer answers one question well.

- `Setup`
  - Which job is running?
  - Where do artifacts go?
  - How many rounds are allowed?
- `plannerskills`
  - What kind of figure is this?
  - Which regions matter?
  - Which capabilities are needed?
- `drawskills`
  - How should layout, text, spacing, containers, and line semantics work?
  - How do we encode that as DrawDSL?
- `visioskills`
  - How do we operate Visio reliably and verifiably?
- `learningskills`
  - What reusable lesson did this round teach us?

Read [AGENT_GUIDE.md](AGENT_GUIDE.md) first if you are an agent entering this repo.

## Repository layout

```text
Setup/          Job config, workspace bootstrapping, execution scripts
plannerskills/  Diagram analysis and orchestration rules
drawskills/     Layout, typography, spacing, DrawDSL, figure-building logic
visioskills/    Visio bridge, atomic operations, operator guidance
learningskills/ Reusable lessons from drawing rounds
InputPNG/       Source figures
OutputPreview/  Preview PNG exports for review
OutputVSDX/     Final VSDX outputs
docs/           Contracts, architecture, setup, workflow docs
```

## Standard artifact chain

For one drawing job, the default chain is:

1. `Setup/draw-job.local.json`
2. `Setup/jobs/<job>/analysis.json`
3. `Setup/jobs/<job>/plan.json`
4. `Setup/jobs/<job>/drawdsl.json`
5. `OutputPreview/<job>/round-*.png`
6. `OutputVSDX/<final>.vsdx`
7. `Setup/jobs/<job>/reviews/round-*.json`
8. `learningskills/lessons/*.md`

This chain is intentional.
Do not collapse everything into one script or one giant prompt.

## Current benchmark

The current main training figure is:

- [InputPNG/1.png](InputPNG/1.png)

We use it to stress:

- mixed layout
- narrow modules
- text-box-size-gap coupling
- container sizing
- connector routing
- preview-based iteration

The benchmark is important, but it is not the end goal.
The real goal is to generalize to new figures later.

## Current capabilities

Implemented or usable now:

- Windows FastAPI bridge to Visio COM
- stable session / save / close / export flow
- node and connector style readback
- page auto-fit before drawing
- text-box coupling
- transparent label shapes
- connector glue-side control
- vertical text support through `DrawDSL -> executor -> bridge -> readback`
- generic layout post-processing for minimum-gap reflow and container auto-fit
- structured round reviews and reusable lessons

Still weak or missing:

- richer connector routing control
- graph-level readback
- image placement
- explicit container membership in more job artifacts
- broader benchmark set across very different figure families

## Quick start

1. Start the Windows bridge.
2. Put the source PNG into `InputPNG/`.
3. Copy `Setup/draw-job.template.json` to `Setup/draw-job.local.json`.
4. Run:

```powershell
python Setup\run_draw_job.py --config Setup\draw-job.local.json
```

5. Then follow:

- [Setup/README.md](Setup/README.md)
- [AGENT_GUIDE.md](AGENT_GUIDE.md)
- [docs/ARTIFACT_CONTRACTS.md](docs/ARTIFACT_CONTRACTS.md)
- [docs/PLAN_TO_OPERATION_LOOP.md](docs/PLAN_TO_OPERATION_LOOP.md)

## What makes this different

- It treats drawing as a closed-loop task, not a one-shot generation task.
- It keeps planning, layout, execution, and learning separate.
- It values human software assets instead of trying to replace them.
- It aims to make the repo itself better every time the agent learns a new fix.

## Project direction

This repo is trying to become a reusable "agentic software layer" over existing high-quality tools.
In this case, the human software asset is Microsoft Visio.
If the system works, the durable value is not one model run.
The durable value is the growing library of:

- contracts
- skills
- operations
- layout rules
- review rules
- lessons

That is the part we want to keep getting stronger.

## Backend direction

The current backend is Microsoft Visio, so the execution layer today is `visioskills`.

The longer-term direction is broader:

- keep `plannerskills` focused on figure understanding and orchestration
- keep `drawskills` focused on backend-neutral drawing intent
- keep `learningskills` focused on reusable failure patterns and lessons
- allow multiple software backends through backend-specific skill layers such as:
  - `visioskills`
  - future `drawioskills`

That means the durable asset should live mostly above any one software backend.
If a new backend is added later, the goal is to swap the execution layer with minimal change to the higher-level cognitive loop.

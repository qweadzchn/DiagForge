# DiagForge

Forge human-editable diagrams through an agentic abstraction layer on top of professional diagram software.

DiagForge is not a one-shot "PNG to VSDX" script.
It is a repository for building a durable Agentic Abstraction Layer for diagram work:

- humans provide rough visual targets and intent
- the model plans and reasons
- software backends provide reliable execution
- preview and runtime feedback drive reflection
- repeated fixes become reusable assets

The goal is to revive dead pixels into structured, editable diagram artifacts that humans can keep refining in tools like Microsoft Visio, and later other diagram backends as well.

## Core idea

The foundation model is the reasoning engine.
The durable value lives around it:

- planning contracts
- layout rules
- drawing DSLs
- software operation layers
- review loops
- reusable lessons

That is the part we want to keep improving even as base models change.

## Why the name `DiagForge`

`Diag` points to the real object we care about:

- diagram logic
- spatial topology
- layout intent
- editable structure

`Forge` points to the working loop:

- take rough human input as raw material
- execute through software skills
- read back environment feedback
- reflect on what failed
- repair the next round
- turn repeated repairs into reusable assets

This is why the repo should not be understood as "export a static picture".
It is about forging live diagram assets through a closed loop.

## What makes this different

Most diagram automation projects stop at one of these points:

- they generate a picture once, but do not improve round by round
- they can click software, but do not know how to draw well
- they run demos, but do not leave behind reusable planning and review assets

DiagForge is trying to build the missing middle layer:

`intent -> plan -> drawdsl -> backend -> preview -> review -> lesson`

That loop is the product.

## The closed loop

DiagForge treats diagram work as two coupled passes:

1. Forward execution
   - analyze the figure
   - plan structure and priorities
   - compile drawing intent into DrawDSL
   - execute through a software backend

2. Backward reflection
   - inspect preview and runtime feedback
   - identify whether failure belongs to planning, layout, or execution
   - update rules, checks, and lessons
   - make the next round measurably better

This is the key idea behind the repo's "agentic abstraction layer" direction.

## Layered architecture

The repo is split into five layers.
Each layer should answer one question well.

- `Setup`
  - Which job is running?
  - Where do artifacts go?
  - How many rounds are allowed?
- `plannerskills`
  - What kind of figure is this?
  - Which regions matter?
  - Which capabilities are needed?
- `drawskills`
  - How should layout, text, spacing, containers, and connector semantics work?
  - How should that be encoded as DrawDSL?
- `visioskills`
  - How do we operate Microsoft Visio reliably and verifiably?
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
Do not collapse everything into one prompt or one script.

## Backend direction

The current execution backend is Microsoft Visio, so the runtime layer today is `visioskills`.

The longer-term direction is broader:

- keep `plannerskills` focused on figure understanding and orchestration
- keep `drawskills` focused on backend-neutral drawing intent
- keep `learningskills` focused on reusable failure patterns and lessons
- support multiple software backends through backend-specific skill layers such as:
  - `visioskills`
  - future `drawioskills`

This does not mean "add one folder and nothing else changes".
It means the higher-level cognitive loop should stay stable while backend-specific execution and capability mapping remain isolated.

## Current capabilities

Implemented or usable now:

- Windows FastAPI bridge to Visio COM
- stable session, save, close, and export flow
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
- native image placement
- broader benchmark coverage across different figure families
- stronger backend abstraction above Visio-specific execution details

## Current benchmark direction

The repository is being trained against benchmark figures under `InputPNG/`.
These figures are not the end goal.
They are pressure tests for the system:

- mixed layout
- narrow modules
- text-box-size-gap coupling
- container sizing
- connector routing
- preview-based iteration
- planner/draw/runtime failure routing

## Quick start

1. Start the Windows bridge.
2. Put the source PNG into `InputPNG/`.
3. Copy `Setup/draw-job.template.json` to `Setup/draw-job.local.json`.
4. Run:

```powershell
python Setup\run_draw_job.py --config Setup\draw-job.local.json
```

Then follow:

- [Setup/README.md](Setup/README.md)
- [AGENT_GUIDE.md](AGENT_GUIDE.md)
- [docs/ARTIFACT_CONTRACTS.md](docs/ARTIFACT_CONTRACTS.md)
- [docs/LAYER_CONTRACTS.md](docs/LAYER_CONTRACTS.md)
- [docs/PLAN_TO_OPERATION_LOOP.md](docs/PLAN_TO_OPERATION_LOOP.md)

## Project direction

DiagForge is trying to become a reusable agentic software layer over existing high-quality human tools.

In the current phase, the human software asset is Microsoft Visio.
Later it may include other diagram software.

If the system works, the durable value is not one model run.
The durable value is the growing library of:

- contracts
- skills
- operations
- layout rules
- review rules
- lessons
- backend adapters

That is the part we want to keep getting stronger.

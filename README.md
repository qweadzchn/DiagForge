# DiagForge

[English](README.md) | [简体中文](README.zh-CN.md)

DiagForge is an experimental framework for turning reference diagrams into editable diagram assets through an agent-guided loop built on top of Microsoft Visio.

Today the project focuses on:

- analyzing a source figure
- planning layout and drawing strategy
- compiling that plan into DrawDSL
- executing through a Visio bridge
- exporting previews, reviewing each round, and carrying lessons forward

The repository is for building the workflow, contracts, and reusable skills around that loop.

## Start Here

- New to the project: [GET_STARTED.md](GET_STARTED.md)
- Running a drawing job: [Setup/README.md](Setup/README.md)
- Onboarding an agent: [AGENT_START_HERE.md](AGENT_START_HERE.md)
- Working on the system itself: [DEVELOPMENT.md](DEVELOPMENT.md)
- Checking run modes and write rules: [MODE_POLICY.md](MODE_POLICY.md)

## What The Repository Tries To Do

DiagForge is not trying to replace professional diagram tools.
It is trying to make them usable through an explicit agent workflow:

`intent -> analysis -> plan -> drawdsl -> backend -> preview -> review -> lesson`

That workflow is split into clear layers so each part can improve without collapsing everything into one prompt.

## Repository Guide

- `Setup/`
  - job config, workspace bootstrap, execution scripts
- `plannerskills/`
  - figure analysis and task orchestration
- `drawskills/`
  - layout, typography, spacing, DrawDSL, drawing rules
- `visioskills/`
  - Visio bridge, atomic operations, operator guidance
- `learningskills/`
  - reusable lessons from drawing rounds
- `docs/`
  - human docs, development docs, architecture docs, research notes

For the detailed agent operating guide, see [AGENT_GUIDE.md](AGENT_GUIDE.md).

## How The Loop Works

1. Analyze the figure and identify its main regions.
2. Plan what should be drawn first and what must improve this round.
3. Compile the drawing intent into DrawDSL.
4. Execute the plan through the software backend.
5. Export a preview and compare it against the target.
6. Record what worked, what failed, and what should become reusable knowledge.

## Current Status

Working now:

- Windows FastAPI bridge to Visio COM
- stable session, save, close, and export flow
- DrawDSL-based node and connector execution
- text-box coupling and vertical text support
- preview-based review workflow
- reusable lessons captured in `learningskills/`

Still incomplete:

- richer connector routing control
- graph-level readback
- native image placement
- broader benchmark coverage
- stronger backend abstraction beyond Visio

## Documentation

- Project index: [docs/README.md](docs/README.md)
- Architecture and contracts: [docs/architecture/README.md](docs/architecture/README.md)
- Human-facing operational docs: [docs/human/README.md](docs/human/README.md)
- Development docs: [docs/dev/README.md](docs/dev/README.md)

## License

DiagForge is released under the MIT License.
See [LICENSE](LICENSE).

## Backend Direction

The current execution backend is Microsoft Visio.
The higher-level goal is to keep planning, drawing intent, review, and learning as stable layers while allowing additional backends in the future, such as a parallel `drawioskills/` layer.

## Project Direction

If this repository is useful over time, the durable value will not be a single model run.
It will be the growing set of:

- contracts
- skills
- operations
- layout rules
- review rules
- lessons
- backend adapters

That is the part the project is trying to make easier to build, test, and reuse.

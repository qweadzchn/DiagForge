# agent/skills

This is the shared skill layer for DrawForge.

The structure is intentionally split by responsibility:

- `plannerskills/`
  - understand the input figure, choose priorities, and decide handoff structure
- `drawskills/`
  - turn plan into layout, spacing, text, and DrawDSL decisions
- `visioskills/`
  - operate Microsoft Visio reliably through explicit low-level controls
- `learningskills/`
  - turn repeated fixes and failures into reusable lessons

If you are onboarding a new agent, this directory is the stable place to start.

Read in this order when needed:

1. `../../AGENT_START_HERE.md`
2. `../../AGENT_GUIDE.md`
3. `plannerskills/README.md`
4. `drawskills/README.md`
5. `visioskills/README.md`
6. `learningskills/README.md`

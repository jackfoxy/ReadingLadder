# FreeCAD MCP project

Conventions for Claude when driving FreeCAD through the AI Copilot MCP server.

## Modeling
- Units are inches unless stated otherwise.
- Always create (or target) a named Body before adding PartDesign features.
- Prefer parametric features (pad, pocket, revolution, fillet, chamfer) over raw
  Part primitives when the design is meant to stay editable.
- Name objects meaningfully (`BasePlate`, `MountHole_1`), not the defaults.

## Files & version control
- The generating script under `src/` is the source of truth, not the `.FCStd`.
- `.FCStd` files in `models/` are committed checkpoints, rebuildable from `src/`.
- Exports go in `build/` and are treated as disposable artifacts.
- STEP for CAD interchange, STL for 3D printing.

## Workflow
- FreeCAD must be running with the AI Copilot workbench active for MCP commands.
- There must be an active document before issuing modeling commands.
- After structural changes, save so the committed checkpoint reflects them.

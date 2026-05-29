# ReadingLadder

A one-piece furniture design: a floor-standing **reading lectern** on the front,
**steps** climbing the back to a **top platform** for reaching high shelves, with
a front **book cubby** (3 compartments), a side-loading **under-step shelf**, and
a platform **grab post**.

Modeled in FreeCAD (driven through the AI Copilot MCP server), script-first, with
Git set up to handle `.FCStd` files sanely.

Design spec (inches): 42" deep × 24" wide footprint; steps 3 × (8" rise / 10"
tread) to a platform at 24"; lectern rises to 46" with a reading surface sloping
to a 42" front lip. Modeling units are inches (`CLAUDE.md`).

## Layout

```
.
├── .gitattributes        # routes .FCStd through the rezip clean/smudge filter
├── .gitignore            # backups, locks, python cache, build/ artifacts
├── CLAUDE.md             # conventions loaded by Claude Code each session
├── README.md
├── tools/
│   ├── fcstd-rezip.py    # git clean filter: stores zip entries uncompressed
│   └── setup-filters.sh  # run once per clone to register the filter
├── src/                  # model-generating scripts -- the source of truth
│   ├── reading_ladder_phase1.py        # massing block (side profile, padded 24")
│   ├── reading_ladder_phase2.py        # hollow into 3/4" panels (shell)
│   ├── reading_ladder_phase3a_cubby.py # front 3-compartment book cubby
│   ├── reading_ladder_phase3b_lip.py   # reading-surface front lip
│   ├── reading_ladder_phase3c_sideshelf.py # left under-step side shelf
│   ├── reading_ladder_phase4_grabpost.py   # platform grab post
│   ├── reading_ladder_phase5_export.py # save + export STEP/STL
│   ├── reading_ladder_parts.py         # all components as flat 3/4" solids
│   ├── reading_ladder_drawings.py      # TechDraw pages (view in FreeCAD GUI)
│   ├── gen_drawings_svg.py             # standalone dimensioned shop-drawing SVGs
│   └── diag.py, diag_faces.py          # inspection helpers
├── docs/
│   └── cutlist.md        # component cut list (3/4" ply + lumber, butt joints)
├── models/               # committed .FCStd checkpoints (rebuildable from src/)
│   ├── ReadingLadder.FCStd        # the assembly
│   └── ReadingLadder_Parts.FCStd  # exploded parts + TechDraw pages
└── build/                # exported STEP / STL / SVG -- ignored, regenerable
```

## First-time setup

```bash
git clone git@github.com:jackfoxy/ReadingLadder.git
cd ReadingLadder
bash tools/setup-filters.sh   # register the .FCStd filter in .git/config
```

`setup-filters.sh` registers the rezip filter (`clean` + a pass-through `smudge`,
`required`). The filter *definition* lives in `.git/config`, which is **not**
version-controlled, so every fresh clone runs it once. Without the `smudge`,
`required = true` makes `.FCStd` checkout/restore (and a fresh clone's checkout)
fail — so don't skip this step. `.gitattributes` (tracked) only says *which*
files use the filter, not what it does.

## Building the model

FreeCAD must be running with the AI Copilot workbench and an active document.
Run each phase from the FreeCAD Python console, in order:

```python
exec(open('/abs/path/to/ReadingLadder/src/reading_ladder_phase1.py').read())
# ...phase2, phase3a, phase3c, phase3b, phase4, phase5
```

Each phase prints a status line and (phase 1) saves `models/ReadingLadder.FCStd`.
Phase 5 exports `build/ReadingLadder.{step,stl}`.

## Component schematics

See the cut list in [`docs/cutlist.md`](docs/cutlist.md) and the assembled
drawings in **[`build/ReadingLadder_drawings.pdf`](build/ReadingLadder_drawings.pdf)**
(11 pages, A4 landscape — one dimensioned page per part).

```python
# in FreeCAD: build the parts model + TechDraw pages
exec(open('/abs/path/to/ReadingLadder/src/reading_ladder_parts.py').read())
exec(open('/abs/path/to/ReadingLadder/src/reading_ladder_drawings.py').read())
```

```bash
# standalone (no FreeCAD): printable A4 dimensioned shop drawings -> build/drawings/
python3 src/gen_drawings_svg.py        # 11 per-part SVGs
python3 src/assemble_drawings_pdf.py   # combine into build/ReadingLadder_drawings.pdf
```

The TechDraw pages render when `ReadingLadder_Parts.FCStd` is opened in the
FreeCAD GUI. TechDraw's *headless* SVG export drops view geometry, so the
**printable** drawings come from `gen_drawings_svg.py`, not the TechDraw export.

## Why this shape

`.FCStd` is a binary zip, so Git can't diff or merge it. Two defenses:

1. **The rezip filter** stores the archive uncompressed on the way into Git, so
   successive commits delta-compress well instead of storing whole new copies.
2. **Script-first**: the `src/` scripts are the source of truth — plain text,
   clean diffs, fully regenerable. The `.FCStd` files in `models/` are
   convenience checkpoints; `build/` holds disposable exports (STEP for
   interchange, STL for printing, SVG shop drawings) and is **gitignored** —
   regenerate from `src/` rather than committing it.

## Notes

- The as-built `.FCStd` carries a known **+¾" outward-shell artifact** (phase 2
  shelled outward), so the assembly is ~43.5 × 25.5 × 60" vs the 42 × 24" spec.
  The **component schematics use the nominal spec**, not the as-built solid.
- `models/ReadingLadder.FCStd` is the assembly; `models/ReadingLadder_Parts.FCStd`
  is the flat exploded parts set used for the cut list and drawings.

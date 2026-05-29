# FreeCAD project scaffold

A script-first layout for FreeCAD work driven through the AI Copilot MCP server,
with Git set up to handle `.FCStd` files sanely.

## Layout

```
.
├── .gitattributes        # routes .FCStd through the rezip clean filter
├── .gitignore            # backups, locks, python cache, optional artifacts
├── CLAUDE.md             # conventions loaded by Claude Code each session
├── README.md
├── tools/
│   ├── fcstd-rezip.py    # git clean filter: stores zip entries uncompressed
│   └── setup-filters.sh  # run once per clone to register the filter
├── src/                  # model-generating scripts -- the real source of truth
│   └── bracket.py
├── models/               # committed .FCStd checkpoints (rebuildable from src/)
└── build/                # exported STEP / STL -- artifacts, optional to track
```

## First-time setup

```bash
git init                      # if this isn't a repo yet
bash tools/setup-filters.sh   # register the clean filter in .git/config
```

The filter definition lives in `.git/config`, which is **not** version-controlled,
so every fresh clone has to run `setup-filters.sh` once. The `.gitattributes`
(which *is* tracked) only says *which* files use the filter, not what it does.

If you add `.FCStd` files before registering the filter, apply it retroactively
with `git add --renormalize .`.

## Why this shape

`.FCStd` is a binary zip, so Git can't diff or merge it. Two defenses:

1. **The rezip filter** stores the archive uncompressed on the way into Git, so
   successive commits delta-compress well instead of storing whole new copies.
2. **Script-first**: keep the *generating script* in `src/` as the source of
   truth. Plain text -- clean diffs, real merges, fully regenerable. The
   `.FCStd` in `models/` is a convenience checkpoint; `build/` holds disposable
   exports (STEP for interchange, STL for printing).

You don't have to commit to script-first immediately -- the filter alone makes
committing `.FCStd` files tolerable. But the more your modeling runs through
Claude / scripts, the more the text in `src/` becomes the thing worth versioning.
```

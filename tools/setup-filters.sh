#!/usr/bin/env bash
# Register the FreeCAD rezip clean filter for THIS repository.
#
# Filter *definitions* live in .git/config, which is NOT version-controlled,
# so .gitattributes alone isn't enough -- every fresh clone must run this once.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"

git config filter.fcstd-rezip.clean "python3 ${repo_root}/tools/fcstd-rezip.py"
# Pass-through smudge: the clean filter already stores a valid (uncompressed)
# zip, so checkout just writes it verbatim. Required because 'required = true'
# below makes Git insist on a smudge command -- without this, checkout/restore
# of a .FCStd (and a fresh clone's initial checkout) fails the filter check.
git config filter.fcstd-rezip.smudge cat
git config filter.fcstd-rezip.required true

echo "Registered fcstd-rezip clean+smudge filter for ${repo_root}"
echo "Tip: 'git add --renormalize .' to apply it to already-tracked .FCStd files."

#!/usr/bin/env bash
# Register the FreeCAD rezip clean filter for THIS repository.
#
# Filter *definitions* live in .git/config, which is NOT version-controlled,
# so .gitattributes alone isn't enough -- every fresh clone must run this once.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"

git config filter.fcstd-rezip.clean "python3 ${repo_root}/tools/fcstd-rezip.py"
git config filter.fcstd-rezip.required true

echo "Registered fcstd-rezip clean filter for ${repo_root}"
echo "Tip: 'git add --renormalize .' to apply it to already-tracked .FCStd files."

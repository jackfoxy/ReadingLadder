#!/usr/bin/env python3
"""Git clean filter for FreeCAD .FCStd files.

A .FCStd file is a zip archive whose entries (mostly XML plus a BREP blob) are
DEFLATE-compressed. Compressed bytes change wholesale even on tiny edits, so
Git stores a fresh copy every commit and the repo balloons.

This clean filter re-writes the archive so every entry is STORED (uncompressed).
The file is byte-for-byte valid and FreeCAD opens STORED zips natively, so no
smudge filter is needed -- but now the inner XML sits verbatim in the object,
and Git's own delta compression can diff successive commits effectively.

It also DROPS FreeCAD's preview thumbnail (thumbnails/Thumbnail.png): FreeCAD
regenerates it on every save, so it is pure binary churn in version control.
The thumbnail is optional -- FreeCAD opens the document fine without it.

Usage (stdin -> stdout), wired up via tools/setup-filters.sh:
    git config filter.fcstd-rezip.clean "python3 .../tools/fcstd-rezip.py"
"""
import io
import sys
import zipfile

# Entries dropped on the way into Git (volatile / regenerated each save).
SKIP_PREFIXES = ("thumbnails/",)


def main() -> None:
    data = sys.stdin.buffer.read()
    src = io.BytesIO(data)

    try:
        zin = zipfile.ZipFile(src)
    except zipfile.BadZipFile:
        # Empty or not actually a zip -- pass through untouched.
        sys.stdout.buffer.write(data)
        return

    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_STORED) as zout:
        for info in zin.infolist():
            if info.filename.startswith(SKIP_PREFIXES):
                continue  # drop the volatile preview thumbnail
            # Read with the ORIGINAL compression, then re-store uncompressed.
            content = zin.read(info.filename)
            info.compress_type = zipfile.ZIP_STORED
            zout.writestr(info, content)

    sys.stdout.buffer.write(out.getvalue())


if __name__ == "__main__":
    main()

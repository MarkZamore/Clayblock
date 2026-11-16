"""Carry Clayblock's native warning preference into reviewed KubeJS defaults."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile

PACK = Path(__file__).resolve().parents[1]
TEMPLATE = "kubejs/config/defaultoptions.txt"
KEY = b"skipMultiplayerWarning:"
REQUIRED = KEY + b"true"


def verify_template(data):
    if [line for line in data.splitlines() if line.startswith(KEY)] != [REQUIRED]:
        raise ValueError(f"{TEMPLATE} must contain exactly one skipMultiplayerWarning:true")
    if any(line.startswith(b"version:") for line in data.splitlines()):
        raise ValueError(f"{TEMPLATE} must let KubeJS write the version header")


def replacements(data):
    """Return exact replacements without changing unrelated rows or CRLF/LF."""
    rows = data.splitlines(keepends=True)
    warning = [line for line in rows if line.startswith(KEY)]
    versions = [line for line in rows if line.startswith(b"version:")]
    if len(warning) > 1 or len(versions) > 1:
        raise ValueError("Ambiguous warning or version rows in the author template")
    if not rows:
        raise ValueError("Empty author template requires review")

    edits = []
    if versions:
        if not re.fullmatch(rb"version:[0-9]+(?:\r?\n)?", versions[0]):
            raise ValueError("Unrecognized KubeJS version header")
        edits.append((versions[0], b""))
    if warning:
        row = warning[0]
        value = row.rstrip(b"\r\n")
        if value != REQUIRED:
            edits.append((row, REQUIRED + row[len(value):]))
    elif versions:
        row = versions[0]
        edits[0] = (row, REQUIRED + row[len(row.rstrip(b"\r\n")):])
    else:
        row = rows[0]
        newline = b"\r\n" if row.endswith(b"\r\n") else b"\n"
        edits.append((row, REQUIRED + newline + row))

    result = data
    encoded = []
    for old, new in edits:
        if result.count(old) != 1 or not result.startswith(old) and b"\n" + old not in result:
            raise ValueError("The exact author template replacement is ambiguous")
        result = result.replace(old, new, 1)
        encoded.append({"from": old.decode("utf-8"), "to": new.decode("utf-8")})
    verify_template(result)
    return result, encoded


def review_update(launcher_source, candidate_lock, archive_path):
    sys.path.insert(0, str(launcher_source / "tools" / "PackData" / "CurseForge"))
    import prepare
    import release_overlay

    candidate = release_overlay.read_lock(candidate_lock, "client-only")
    current = release_overlay.read_lock(PACK / release_overlay.CLIENT_LOCK, "client-only")
    recipe, _, _, _ = release_overlay.source_policy(PACK, current)
    prepare.require(candidate["client"]["projectId"] == current["client"]["projectId"] and
                    all(candidate["pack"][key] == current["pack"][key] for key in ("minecraftVersion", "loader")),
                    "Review required for a changed author project or game platform")
    with archive_path.open("rb") as source:
        prepare.require(archive_path.stat().st_size == candidate["client"]["sizeBytes"] and
                        hashlib.file_digest(source, "sha256").hexdigest() == candidate["client"]["sha256"],
                        "Candidate archive differs from its author lock")
    rows = [row for row in candidate["overrides"] if row["path"] == TEMPLATE]
    prepare.require(len(rows) == 1, f"Missing {TEMPLATE}: review the author's replacement for KubeJS defaults")
    row, = rows
    with ZipFile(archive_path) as archive:
        members = prepare.archive_members(archive)
        member = members.get(prepare.safe_path(row["archivePath"]))
        prepare.require(member is not None and member.file_size <= prepare.MAX_JSON,
                        "Missing or oversized candidate KubeJS template")
        data = archive.read(member)
    before = {key: row[key] for key in ("sizeBytes", "sha256")}
    prepare.require(prepare.fingerprint(data) == before, "Candidate template differs from its author lock")
    result, edits = replacements(data)

    patches = [patch for patch in recipe["patches"] if patch["path"] != TEMPLATE]
    if edits:
        operation = edits[0] if len(edits) == 1 else {"replacements": edits}
        patches.append({"path": TEMPLATE, "before": before, "after": prepare.fingerprint(result), **operation})
    proposed = {**recipe, "authorArchiveSha256": candidate["client"]["sha256"], "patches": patches}
    release_overlay.patch_inputs(proposed, candidate)
    prepare.overlay_additions(proposed, PACK, candidate)

    owned = set((PACK / release_overlay.OWNERSHIP).read_text(encoding="utf-8").splitlines())
    owned.discard(TEMPLATE)
    if edits:
        owned.add(TEMPLATE)
    return {"overlay": proposed, "packOwnedTxt": "\n".join(sorted(owned)) + "\n"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launcher-source", type=Path, required=True)
    parser.add_argument("--candidate-lock", type=Path, required=True)
    parser.add_argument("--client-archive", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(review_update(args.launcher_source.resolve(), args.candidate_lock, args.client_archive),
                     ensure_ascii=False, indent=2))

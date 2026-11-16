"""Stage a locked Clayblock release with its separately verified launcher preset."""

import argparse
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from multiplayer_warning import TEMPLATE, verify_template

PACK = Path(__file__).resolve().parents[1]
PRESET = "launcher/controls-preset.txt"


def stage_release(launcher_source, stage, output, revision):
    sys.path.insert(0, str(launcher_source / "tools" / "PackData" / "CurseForge"))
    import stage_release as normal
    from prepare import fingerprint, require, write_json

    sys.path.insert(0, str(PACK / "tools" / "keybinds"))
    from check_preset import check

    check()
    verify_template((stage / "game" / TEMPLATE).read_bytes())
    preset = (PACK / PRESET).read_bytes()
    require(preset == normal.git(PACK, "cat-file", "blob", f"{revision}:{PRESET}"),
            "Preset differs from the selected Git revision")
    require(output.parent.is_dir() and not output.exists(), "Use a new release output directory")
    pin = fingerprint(preset)

    with TemporaryDirectory(dir=output.parent, prefix=".clayblock-release-") as scratch:
        pending = Path(scratch) / "release"
        manifest = normal.build_release(PACK, stage, pending, revision, "minecraft-22")
        warning_asset, = (asset for asset in manifest["assets"] if TEMPLATE in asset["covers"])
        with ZipFile(pending / "assets" / warning_asset["name"]) as archive:
            verify_template(archive.read(TEMPLATE))
        require(not any(row["path"].casefold() == PRESET.casefold() for row in manifest["files"]),
                "The author payload already owns the controls preset path")
        assets = normal.build_assets(PACK, pending / "assets", {PRESET: pin})
        require(len(assets) == 1 and assets[0]["covers"] == [PRESET], "Missing standalone controls archive")
        with ZipFile(pending / "assets" / assets[0]["name"]) as archive:
            require(archive.namelist() == [PRESET] and archive.read(PRESET) == preset,
                    "Packaged controls differ from source")
        manifest["files"] = sorted([*manifest["files"], {"path": PRESET, **pin}], key=lambda row: row["path"])
        manifest["assets"] = sorted([*manifest["assets"], *assets], key=lambda row: row["name"])
        manifest_path = pending / "pack-manifest.json"
        updated = pending / "pack-manifest.new.json"
        write_json(updated, manifest)
        updated.replace(manifest_path)
        pending.rename(output)
    return pin


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launcher-source", type=Path, required=True)
    parser.add_argument("--stage", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    print(stage_release(args.launcher_source.resolve(), args.stage.resolve(), args.output.resolve(), args.revision))

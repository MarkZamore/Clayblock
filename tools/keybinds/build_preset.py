"""Build the Clayblock preset from the options saved by the reviewed client."""

from pathlib import Path

HERE = Path(__file__).resolve().parent
PRESET = HERE.parents[1] / "launcher" / "controls-preset.txt"

# All names in the vanilla Options registry retain their original assignments.
# Keys listed here replace only the overlapping or ambiguous mod shortcuts.
CHANGES = {
    "key.trashslot.toggle": "insert",
    "key.trashslot.delete_all": "end",
    "key.craftingtweaks.compress_one": "keypad.divide",
    "key.craftingtweaks.compress_stack": "keypad.multiply",
    "key.craftingtweaks.compress_all": "keypad.subtract",
    "key.craftingtweaks.refill_last": "comma",
    "key.craftingtweaks.refill_last_stack": "period",
    "key.rehooked.fire_hook_key": "mouse.4",
    "key.rehooked.retract_hook_key": "mouse.5",
    "key.rehooked.remove_all_hooks_key": "n",
    "key.sophisticatedcore.sort": "keypad.enter",
    "iris.keybind.reload": "f12",
    "iris.keybind.shaderPackSelection": "right.control",
    "key.shulkerboxslot.open.desc": "h",
    "key.smartcrafting.open_smart_crafting_menu": "k",
    "key.findme.pull_one": "keypad.6",
    "key.findme.pull_stack": "keypad.7",
    "key.sophisticatedsorter.sort": "semicolon",
    "key.sophisticatedsorter.disable": "apostrophe",
    "key.modern_industrialization.toggle_3x3": "minus",
    "key.nextDestination": "right",
    "key.prevDestination": "left",
    "key.guideme.guide": "equal",
    "key.jade.show_details": "caps.lock",
    "ponder.keyinfo.ponder": "grave.accent",
    "key.effortlessbuilding.undo.desc": "z",
    "key.effortlessbuilding.redo.desc": "keypad.equal",
    "key.openManual": "scroll.lock",
    "schematicannon.keyinfo.toolmenu": "home",
    "schematicannon.keyinfo.toolbelt": "right.alt",
    "gui.xaero_minimap_settings": "left.bracket",
    "gui.xaero_instant_waypoint": "keypad.decimal",
    "gui.xaero_enlarge_map": "f8",
    "gui.xaero_waypoints_key": "i",
    "key.jei.focusSearch": "enter:CONTROL",
    "key.jei.toggleHideIngredient": "pause:CONTROL",
    "key.jei.cheatOneItem": "f6",
    "key.jei.cheatOneItem2": "f7",
    "key.jei.cheatItemStack": "f9",
    "key.jei.cheatItemStack2": "f10",
}


def snapshot():
    rows = [line.split("\t") for line in (HERE / "registered-keys.tsv").read_text(encoding="utf-8").splitlines()]
    entries = dict(rows)
    if len(entries) != len(rows) or not CHANGES.keys() <= entries.keys():
        raise ValueError("Duplicate mappings or unknown changes in the registry")
    return entries


def key_value(shortcut):
    if shortcut.startswith("mouse."):
        return "key." + shortcut
    return "key.keyboard." + shortcut


def render():
    entries = snapshot()
    entries.update({name: key_value(value) for name, value in CHANGES.items()})
    return ("# Clayblock 1.3.2 - Minecraft 1.21.1 / NeoForge 21.1.219\n"
            + "".join(f"key_{name}:{value}\n" for name, value in entries.items())).encode("utf-8")


if __name__ == "__main__":
    PRESET.write_bytes(render())

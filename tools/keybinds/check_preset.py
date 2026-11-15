"""Validate the complete Clayblock preset without starting Minecraft."""

from itertools import combinations
import re

from build_preset import CHANGES, PRESET, render, snapshot

MAPPING = re.compile(
    r"key_([^:]+):(key\.(?:keyboard|mouse)\.[a-z0-9.]+)(?::(SHIFT|CONTROL|ALT))?"
)
UNBOUND = "key.keyboard.unknown"
VANILLA_LAST = "key.hotbar.9"
MODIFIERS = {
    "SHIFT": {"key.keyboard.left.shift", "key.keyboard.right.shift"},
    "CONTROL": {"key.keyboard.left.control", "key.keyboard.right.control"},
    "ALT": {"key.keyboard.left.alt", "key.keyboard.right.alt"},
}

# JEI receives mouse input on a Screen. Vanilla attack/use run with the mouse
# grabbed in the world. JEI bookmark on A is similarly separate from movement.
WORLD_INPUT = {"key.attack", "key.use", "key.left", "key.sprint", "key.sneak"}
WORLD_MODIFIERS = {"iris.keybind.shaderPackSelection", "gui.xaero_quick_confirm"}
SCREEN_AREAS = {
    frozenset(("key.jei.showUses2", "key.jei.clearSearchBar")),
    frozenset(("key.jei.maxTransferRecipeBookmark", "key.jei.toggleCheatModeConfigButton")),
}


def overlap(left, right):
    name, key, modifier = left
    other, other_key, other_modifier = right
    if UNBOUND in (key, other_key):
        return False
    if other.startswith("key.jei.") and name in WORLD_INPUT | WORLD_MODIFIERS:
        return False
    if name.startswith("key.jei.") and other in WORLD_INPUT | WORLD_MODIFIERS:
        return False
    if key in MODIFIERS.get(other_modifier, ()) or other_key in MODIFIERS.get(modifier, ()):
        return True
    if key != other_key:
        return False
    if name.startswith("key.jei.") and other.startswith("key.jei."):
        if frozenset((name, other)) in SCREEN_AREAS:
            return False
        return modifier == other_modifier
    return True


def check():
    if PRESET.read_bytes() != render():
        raise ValueError("Preset differs from the generator. Rebuild controls-preset.txt.")

    defaults = snapshot()
    names = tuple(defaults)
    vanilla = set(names[:names.index(VANILLA_LAST) + 1])
    if vanilla & CHANGES.keys():
        raise ValueError("The preset changes vanilla controls.")

    entries = []
    for line in PRESET.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue
        match = MAPPING.fullmatch(line)
        if not match:
            raise ValueError(f"Invalid preset line: {line}")
        entries.append(match.groups())
    if tuple(entry[0] for entry in entries) != names:
        raise ValueError("Preset and registry contain different mappings.")

    issues = [f"{left[0]} / {right[0]}" for left, right in combinations(entries, 2) if overlap(left, right)]
    if issues:
        raise ValueError("Overlapping mappings:\n" + "\n".join(issues))
    print(f"{len(entries)} mappings, {len(vanilla)} unchanged vanilla controls, no modeled conflicts")


if __name__ == "__main__":
    check()

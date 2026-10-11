# GTS Free Travel

Gives you back vanilla fast travel and the "you are here" marker on the map in a
[Gate to Sovngarde](https://www.nexusmods.com/skyrimspecialedition/mods/97490) setup, without
removing any mod from the collection.

> **Status:** version 1.0.0 is built and its plugins pass the loading checks in `test/`, but it has
> not been play-tested in the game yet.

## What it changes

| Feature in the collection | Comes from | What this mod does |
|---|---|---|
| Fast travel needs a travel pack | Journeyman (`Journeyman.dll`) | Replaces the DLL with one that does nothing |
| Your position is hidden on the map | Get Lost (`GetLost.dll`) | Replaces the DLL with one that does nothing |
| Fast travel is disabled in Survival Mode | Survival Mode Improved (`SurvivalModeImproved.ini`) | Ships the same ini with `bDisableFastTravel=0` |

Everything else those three mods add stays: their plugins (`.esp`), scripts, items and recipes.
That matters because other mods and patches in the collection list `Journeyman.esp` as a master,
so uninstalling Journeyman breaks the load order. Travel packs can still be crafted; they just are
not needed any more.

## Why it works this way

Journeyman and Get Lost have no setting to switch them off. Their behaviour lives in a script
extender plugin (a DLL), and the game loads whichever file with that name ends up in
`Data\SKSE\Plugins`. This mod ships two tiny plugins under the same names that register with SKSE
and then do nothing. As long as this mod wins the file conflict, the originals are never loaded.

Because the override is a normal file conflict, it survives a collection update or a reinstall of
those mods. Renaming or deleting the original DLLs by hand does not.

## Requirements

- Skyrim Special Edition with SKSE. Works on 1.5.97, 1.6.x and Skyrim VR: the replacement plugins
  touch no game code, so they do not depend on the game version or on Address Library.
- Journeyman, Get Lost and Survival Mode Improved installed (they are part of Gate to Sovngarde).
  If one of them is missing, the matching file here simply does nothing.

## Install

1. Install with your mod manager like any other mod.
2. Make sure it **overrides** Journeyman, Get Lost and Survival Mode Improved:
   - **Vortex**: when the file-conflict notification appears, set *GTS Free Travel* to load
     **after** each of the three.
   - **Mod Organizer 2**: place it below them in the left pane.
3. Deploy and start the game through SKSE as usual.

## Check that it is active

After starting the game, open `Documents\My Games\Skyrim Special Edition\SKSE\skse64.log`.
You should see lines like:

```
plugin Journeyman.dll (00000001 Journeyman (disabled by GTS Free Travel) 00000001) loaded correctly
plugin GetLost.dll (00000001 GetLost (disabled by GTS Free Travel) 00000001) loaded correctly
```

If the original names appear instead, this mod is not winning the conflict.

## Uninstall

Remove the mod and deploy. The original DLLs and ini take over again; nothing is baked into the save.

## Notes

- `SurvivalModeImproved.ini` is the file from Survival Mode Improved 1.6.6 with one value changed.
  If a later version of that mod adds settings, they will be missing from this copy until it is
  updated.
- Get Lost's Papyrus function `GetLost.RevealMapMarkersOnMap` is not available while its DLL is
  replaced. Scripts that call it will log an error and carry on.

## Build from source

`build.bat` compiles `src\stub.c` twice with the MSVC x64 build tools and puts the result in
`dist\SKSE\Plugins`. `python test\check_stubs.py` loads both DLLs and checks what they report to
SKSE. `python package.py` writes the installable zip to `release\`.

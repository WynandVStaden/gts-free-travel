# GTS Free Travel

Gives you back vanilla fast travel and the "you are here" marker on the map in a
[Gate to Sovngarde](https://www.nexusmods.com/skyrimspecialedition/mods/97490) setup, without
removing any mod from the collection.

**Download:** [Nexus Mods](https://www.nexusmods.com/skyrimspecialedition/mods/194952) or the [releases](https://github.com/WynandVStaden/gts-free-travel/releases) here.

> **Status:** version 1.1.0 passes the loading checks in `test/` and was tested in game on
> 12 October 2026 on a Gate to Sovngarde setup (Skyrim 1.6.1170, Survival Mode Improved 1.6.6).

## What it changes

| Feature in the collection | Comes from | What this mod does |
|---|---|---|
| Fast travel needs a travel pack | Journeyman (`Journeyman.dll`) | Replaces the DLL with one that does nothing |
| Your position is hidden on the map | Get Lost (`GetLost.dll`) | Replaces the DLL with one that does nothing |
| Fast travel is disabled in Survival Mode | Survival Mode Improved (`SurvivalModeImproved.ini`) | Sets `bDisableFastTravel=0` in that ini every time the game starts |

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
  touch no game code or memory, so they do not depend on the game version or on Address Library.
- Journeyman and Get Lost installed (they are part of Gate to Sovngarde). If one of them is
  missing, the matching file here simply does nothing.

## Install

1. Install with your mod manager like any other mod.
2. Make sure it **overrides** Journeyman and Get Lost:
   - **Vortex**: when the file-conflict notification appears, set *GTS Free Travel* to load
     **after** both.
   - **Mod Organizer 2**: place it below them in the left pane.
3. Deploy and start the game through SKSE as usual.

There is nothing to edit by hand. See "The Survival Mode Improved setting" below for what happens
to its ini.

## The Survival Mode Improved setting

Survival Mode Improved blocks fast travel with `bDisableFastTravel=1` in its
`SurvivalModeImproved.ini`. That file belongs to another author, so it is not shipped here.
Instead, each replacement plugin checks that ini when the game loads it and, if the value is not
`0`, rewrites that single line. Nothing else in the file is touched, and if the value is already
`0` the file is not written at all. This happens before Survival Mode Improved itself is loaded,
and it repeats on every start, so an update or reinstall of Survival Mode Improved cannot switch
fast travel off again.

If you use Mod Organizer 2, the changed ini ends up in your Overwrite folder, as with any file a
plugin writes.

## Check that it is active

After starting the game, open `Documents\My Games\Skyrim Special Edition\SKSE\skse64.log`.
You should see lines like:

```
plugin Journeyman.dll (00000001 Journeyman (disabled by GTS Free Travel) 00000001) loaded correctly
plugin GetLost.dll (00000001 GetLost (disabled by GTS Free Travel) 00000001) loaded correctly
```

If the original names appear instead, this mod is not winning the conflict.

## Uninstall

Remove the mod and deploy. The original DLLs take over again; nothing is baked into the save. The
ini keeps `bDisableFastTravel=0`; set it back to `1` if you want Survival Mode to block fast
travel again.

## Notes

- Get Lost's Papyrus function `GetLost.RevealMapMarkersOnMap` is not available while its DLL is
  replaced. Scripts that call it will log an error and carry on.

## Build from source

`build.bat` compiles `src\stub.c` twice with the MSVC x64 build tools and puts the result in
`dist\SKSE\Plugins`. `python test\check_stubs.py` loads both DLLs and checks what they report to
SKSE. `python package.py` writes the installable zip to `release\`.

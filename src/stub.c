/*
 * A script extender plugin that does (almost) nothing.
 *
 * It is built under the file name of another mod's plugin (Journeyman.dll,
 * GetLost.dll) and installed so that it wins the file conflict. The game then
 * loads this instead of the original, which switches that plugin off without
 * removing the mod: its .esp, scripts and assets stay in place, so patches
 * that list them as masters keep working.
 *
 * The one thing it does: when it is loaded it makes sure fast travel is enabled
 * in Survival Mode Improved's ini, see enable_fast_travel_in_survival_mode().
 *
 * No game code or data is touched, so one binary works on every runtime:
 *   - Skyrim SE 1.6.x (AE): SKSE reads the exported SKSEPlugin_Version data.
 *   - Skyrim SE 1.5.97 and Skyrim VR: SKSE calls the exported SKSEPlugin_Query.
 *
 * Build with STUB_NAME set to the plugin name to report, see build.bat.
 */

#ifndef STUB_NAME
#error "define STUB_NAME, e.g. /DSTUB_NAME=\"Journeyman\""
#endif

#define WIN32_LEAN_AND_MEAN
#include <windows.h>

typedef unsigned int UInt32;

#define STUB_VERSION 2

/* ---- Skyrim SE 1.6.x: version data read by SKSE before the DLL is loaded ---- */

enum {
    kVersionIndependent_Signatures = 1 << 1,   /* no hardcoded addresses */
    kVersionIndependentEx_NoStructUse = 1 << 0 /* no game structures used */
};

typedef struct {
    UInt32 dataVersion;
    UInt32 pluginVersion;
    char name[256];
    char author[256];
    char supportEmail[252];
    UInt32 versionIndependenceEx;
    UInt32 versionIndependence;
    UInt32 compatibleVersions[16];
    UInt32 seVersionRequired;
} SKSEPluginVersionData;

__declspec(dllexport) SKSEPluginVersionData SKSEPlugin_Version = {
    1, /* SKSEPluginVersionData::kVersion */
    STUB_VERSION,
    STUB_NAME " (disabled by GTS Free Travel)",
    "WynandVStaden",
    "",
    kVersionIndependentEx_NoStructUse,
    kVersionIndependent_Signatures,
    {0},
    0,
};

/* ---- Skyrim SE 1.5.97 and Skyrim VR: query function called by SKSE ---- */

typedef struct {
    UInt32 infoVersion;
    const char *name;
    UInt32 version;
} PluginInfo;

__declspec(dllexport) int SKSEPlugin_Query(const void *skse, PluginInfo *info) {
    (void)skse;
    info->infoVersion = 1; /* PluginInfo::kInfoVersion */
    info->name = STUB_NAME " (disabled by GTS Free Travel)";
    info->version = STUB_VERSION;
    return 1;
}

/* ---- every runtime ---- */

/*
 * Survival Mode Improved blocks fast travel with `bDisableFastTravel=1` in
 * SurvivalModeImproved.ini, which sits next to this DLL. Set it to 0.
 *
 * Only that one value is rewritten, and only if it is not 0 already; the rest
 * of the file, comments included, is left as it is. If the ini does not exist
 * (Survival Mode Improved is not installed) nothing happens.
 *
 * This runs when the DLL is loaded into the game (DllMain). SKSE loads plugins
 * in alphabetical order, so GetLost.dll and Journeyman.dll get here before
 * SurvivalModeImproved.dll is loaded and reads its settings. Only kernel32
 * file functions are used, which is safe to do from DllMain.
 */
static void enable_fast_travel_in_survival_mode(void) {
    static const char ini_name[] = "SurvivalModeImproved.ini";
    char path[MAX_PATH];
    HMODULE self = NULL;
    DWORD length;
    DWORD i;

    if (!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                            (LPCSTR)&SKSEPlugin_Version, &self)) {
        return;
    }
    length = GetModuleFileNameA(self, path, MAX_PATH);
    if (length == 0 || length >= MAX_PATH) {
        return;
    }
    /* keep the directory, drop this DLL's file name */
    while (length > 0 && path[length - 1] != '\\' &&path[length - 1] != '/') {
        length--;
    }
    if (length + sizeof(ini_name) > MAX_PATH) {
        return;
    }
    for (i = 0; i < sizeof(ini_name); i++) {
        path[length + i] = ini_name[i];
    }

    if (GetFileAttributesA(path) == INVALID_FILE_ATTRIBUTES) {
        return;
    }
    if (GetPrivateProfileIntA("General", "bDisableFastTravel", 0, path) != 0) {
        WritePrivateProfileStringA("General", "bDisableFastTravel", "0", path);
    }
}

__declspec(dllexport) int SKSEPlugin_Load(const void *skse) {
    (void)skse;
    return 1;
}

BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved) {
    (void)instance;
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        enable_fast_travel_in_survival_mode();
    }
    return TRUE;
}

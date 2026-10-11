/*
 * A script extender plugin that does nothing.
 *
 * It is built under the file name of another mod's plugin (Journeyman.dll,
 * GetLost.dll) and installed so that it wins the file conflict. The game then
 * loads this instead of the original, which switches that plugin off without
 * removing the mod: its .esp, scripts and assets stay in place, so patches
 * that list them as masters keep working.
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

typedef unsigned int UInt32;

#define STUB_VERSION 1

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

__declspec(dllexport) int SKSEPlugin_Load(const void *skse) {
    (void)skse;
    return 1;
}

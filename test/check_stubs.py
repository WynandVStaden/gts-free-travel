"""Load the built plugins the way SKSE does and check what they report and do.

Run with a 64-bit Python:  python test/check_stubs.py
"""
import ctypes
import pathlib
import shutil
import struct
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "dist" / "SKSE" / "Plugins"

KVERSION_INDEPENDENT_SIGNATURES = 1 << 1
KVERSION_INDEPENDENT_EX_NO_STRUCT_USE = 1 << 0

# Same shape as Survival Mode Improved's ini: '#' comments, a blank line, more sections.
SAMPLE_INI = (
    "[General]\n"
    "#Toggle setting for disabling fast travel \n"
    "bDisableFastTravel={value}\n"
    "\n"
    "#Toggle setting to automatically start Survival Mode\n"
    "bAutoEnableSMOnNewGame=1\n"
    ";Injury Settings\n"
    "fInjury1AVPercent=0.10\n"
    "[Cold Settings]\n"
    "fBlizzardWindSpeedThreshold=150.0\n"
)


class SKSEPluginVersionData(ctypes.Structure):
    _fields_ = [
        ("dataVersion", ctypes.c_uint32),
        ("pluginVersion", ctypes.c_uint32),
        ("name", ctypes.c_char * 256),
        ("author", ctypes.c_char * 256),
        ("supportEmail", ctypes.c_char * 252),
        ("versionIndependenceEx", ctypes.c_uint32),
        ("versionIndependence", ctypes.c_uint32),
        ("compatibleVersions", ctypes.c_uint32 * 16),
        ("seVersionRequired", ctypes.c_uint32),
    ]


class PluginInfo(ctypes.Structure):
    _fields_ = [
        ("infoVersion", ctypes.c_uint32),
        ("name", ctypes.c_char_p),
        ("version", ctypes.c_uint32),
    ]


def imported_dlls(path: pathlib.Path) -> set[str]:
    """Names of the DLLs a PE32+ file imports, lower case."""
    data = path.read_bytes()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    assert data[pe:pe + 4] == b"PE\0\0"
    assert struct.unpack_from("<H", data, pe + 4)[0] == 0x8664, f"{path.name} is not x64"
    section_count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    optional = pe + 24
    assert struct.unpack_from("<H", data, optional)[0] == 0x20B  # PE32+
    import_rva = struct.unpack_from("<I", data, optional + 112 + 8)[0]
    sections = []
    for i in range(section_count):
        off = optional + optional_size + 40 * i
        vsize, vaddr, rsize, raddr = struct.unpack_from("<IIII", data, off + 8)
        sections.append((vaddr, max(vsize, rsize), raddr))

    def offset(rva: int) -> int:
        for vaddr, size, raddr in sections:
            if vaddr <= rva < vaddr + size:
                return rva - vaddr + raddr
        raise ValueError(hex(rva))

    names = set()
    if import_rva:
        entry = offset(import_rva)
        while True:
            name_rva = struct.unpack_from("<I", data, entry + 12)[0]
            if not name_rva:
                break
            start = offset(name_rva)
            names.add(data[start:data.index(b"\0", start)].decode().lower())
            entry += 20
    return names


def load_copy(name: str, folder: pathlib.Path) -> ctypes.CDLL:
    """Copy the plugin into `folder` (its stand-in for Data\\SKSE\\Plugins) and load it."""
    target = folder / f"{name}.dll"
    shutil.copy2(PLUGINS / f"{name}.dll", target)
    dll = ctypes.CDLL(str(target))
    dll.SKSEPlugin_Load.restype = ctypes.c_int
    dll.SKSEPlugin_Query.restype = ctypes.c_int
    return dll


def unload(dll: ctypes.CDLL) -> None:
    ctypes.windll.kernel32.FreeLibrary.argtypes = [ctypes.c_void_p]
    ctypes.windll.kernel32.FreeLibrary(dll._handle)


def check_reports(name: str) -> None:
    assert imported_dlls(PLUGINS / f"{name}.dll") <= {"kernel32.dll"}, "unexpected DLL dependency"
    with tempfile.TemporaryDirectory() as tmp:
        dll = load_copy(name, pathlib.Path(tmp))
        expected = f"{name} (disabled by GTS Free Travel)".encode()

        # Skyrim SE 1.6.x
        version = SKSEPluginVersionData.in_dll(dll, "SKSEPlugin_Version")
        assert ctypes.sizeof(version) == 0x350
        assert version.dataVersion == 1
        assert version.name == expected, version.name
        assert version.versionIndependence == KVERSION_INDEPENDENT_SIGNATURES
        assert version.versionIndependenceEx == KVERSION_INDEPENDENT_EX_NO_STRUCT_USE
        assert list(version.compatibleVersions) == [0] * 16
        assert version.seVersionRequired == 0

        # Skyrim SE 1.5.97 and Skyrim VR
        info = PluginInfo()
        assert dll.SKSEPlugin_Query(None, ctypes.byref(info)) == 1
        assert info.infoVersion == 1 and info.name == expected and info.version == 2

        # No Survival Mode Improved ini next to the plugin: loading must not create one.
        assert dll.SKSEPlugin_Load(None) == 1
        assert sorted(p.name for p in pathlib.Path(tmp).iterdir()) == [f"{name}.dll"]
        unload(dll)


def check_ini(name: str) -> None:
    # Fast travel disabled: exactly that one line changes.
    with tempfile.TemporaryDirectory() as tmp:
        folder = pathlib.Path(tmp)
        ini = folder / "SurvivalModeImproved.ini"
        ini.write_text(SAMPLE_INI.format(value=1), newline="\r\n")
        dll = load_copy(name, folder)
        # The fix happens when the DLL is loaded, before SKSE calls anything in it.
        after = ini.read_text().splitlines()
        assert after == SAMPLE_INI.format(value=0).splitlines(), after
        assert dll.SKSEPlugin_Load(None) == 1
        unload(dll)
        after = ini.read_text().splitlines()
        assert after == SAMPLE_INI.format(value=0).splitlines(), after

    # Already enabled: the file is not written at all.
    with tempfile.TemporaryDirectory() as tmp:
        folder = pathlib.Path(tmp)
        ini = folder / "SurvivalModeImproved.ini"
        ini.write_text(SAMPLE_INI.format(value=0), newline="\r\n")
        before = (ini.read_bytes(), ini.stat().st_mtime_ns)
        dll = load_copy(name, folder)
        assert dll.SKSEPlugin_Load(None) == 1
        unload(dll)
        assert (ini.read_bytes(), ini.stat().st_mtime_ns) == before


if __name__ == "__main__":
    assert struct.calcsize("P") == 8, "needs a 64-bit Python"
    for plugin in ("Journeyman", "GetLost"):
        check_reports(plugin)
        check_ini(plugin)
        print(f"ok  {plugin}.dll  ({(PLUGINS / (plugin + '.dll')).stat().st_size} bytes)")
    sys.exit(0)

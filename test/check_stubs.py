"""Load the built plugins the way SKSE does and check what they report.

Run with a 64-bit Python:  python test/check_stubs.py
"""
import ctypes
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "dist" / "SKSE" / "Plugins"

KVERSION_INDEPENDENT_SIGNATURES = 1 << 1
KVERSION_INDEPENDENT_EX_NO_STRUCT_USE = 1 << 0


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


def imports_of(path: pathlib.Path) -> int:
    """Size of the PE import directory; 0 means the DLL depends on nothing."""
    data = path.read_bytes()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    assert data[pe:pe + 4] == b"PE\0\0"
    machine = struct.unpack_from("<H", data, pe + 4)[0]
    assert machine == 0x8664, f"{path.name} is not x64"
    optional = pe + 24
    assert struct.unpack_from("<H", data, optional)[0] == 0x20B  # PE32+
    return struct.unpack_from("<I", data, optional + 112 + 8 + 4)[0]


def check(name: str) -> None:
    path = PLUGINS / f"{name}.dll"
    assert imports_of(path) == 0, f"{name}.dll imports other DLLs"

    dll = ctypes.CDLL(str(path))
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
    dll.SKSEPlugin_Query.restype = ctypes.c_int
    assert dll.SKSEPlugin_Query(None, ctypes.byref(info)) == 1
    assert info.infoVersion == 1 and info.name == expected and info.version == 1

    dll.SKSEPlugin_Load.restype = ctypes.c_int
    assert dll.SKSEPlugin_Load(None) == 1

    print(f"ok  {name}.dll  ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    assert struct.calcsize("P") == 8, "needs a 64-bit Python"
    for plugin in ("Journeyman", "GetLost"):
        check(plugin)
    sys.exit(0)

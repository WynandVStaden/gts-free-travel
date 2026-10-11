"""Write the installable archive: release/GTS Free Travel-<version>.zip"""
import pathlib
import zipfile

VERSION = "1.0.1"
ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT / "dist"
FILES = [
    "SKSE/Plugins/Journeyman.dll",
    "SKSE/Plugins/GetLost.dll",
]

out = ROOT / "release" / f"GTS Free Travel-{VERSION}.zip"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
    for name in FILES:
        archive.write(DIST / name, name)
print(out, out.stat().st_size, "bytes")

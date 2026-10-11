@echo off
rem Builds the two no-op plugins into dist\SKSE\Plugins.
rem Needs the MSVC x64 build tools (run from any prompt; vcvars is called here).
setlocal

set "VCVARS=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
if not exist "%VCVARS%" set "VCVARS=C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
call "%VCVARS%" >nul || exit /b 1

set "ROOT=%~dp0"
set "OUT=%ROOT%dist\SKSE\Plugins"
set "OBJ=%ROOT%build"
if not exist "%OUT%" mkdir "%OUT%"
if not exist "%OBJ%" mkdir "%OBJ%"

for %%N in (Journeyman GetLost) do (
    cl /nologo /O1 /GS- /W4 /WX /c /DSTUB_NAME=\"%%N\" /Fo"%OBJ%\%%N.obj" "%ROOT%src\stub.c" || exit /b 1
    link /nologo /DLL /NOENTRY /NODEFAULTLIB /MACHINE:X64 /OUT:"%OUT%\%%N.dll" /IMPLIB:"%OBJ%\%%N.lib" "%OBJ%\%%N.obj" || exit /b 1
)

echo Built:
dir /b "%OUT%\*.dll"

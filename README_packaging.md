# Packaging fil2mid to a Windows EXE

This project provides a simple packaging script (`pack.ps1` and `pack.bat`) that uses the Python virtualenv to build a single-file Windows executable using PyInstaller.

Quick steps (PowerShell):

```powershell
cd C:\Users\josep\OneDrive\Documents\Projects\Disklavear
./pack.ps1
```

Or in cmd.exe:

```bat
cd C:\Users\josep\OneDrive\Documents\Projects\Disklavear
pack.bat
```

If you prefer not to have the script install packages, pass `-SkipInstall` when running `pack.ps1`.
If you don't have a `requirements.txt` and would like the script to create a simple one for you, pass `-AutoCreateRequirements`.

Important:
- Run the packaging command from the repository root. If you run from `.venv\Scripts` and provide a relative path, PyInstaller will not find the script and will raise an error like `Script file 'tools\convert_fil_to_mid.py' does not exist.`
- If you see errors about missing modules, add them to `requirements.txt` and re-run.
- If your target machine is different, build on an OS similar to the target (for native libraries with python-rtmidi).

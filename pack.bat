@echo off
REM Simple packaging helper: installs requirements and builds a single-file exe using PyInstaller.
REM Change to script directory so relative paths resolve consistently
pushd %~dp0
python -m pip install -r requirements.txt
pyinstaller --onefile --name fil2mid fil2mid.py
IF ERRORLEVEL 1 (
    echo Build failed
    popd
    exit /b 1
) ELSE (
    echo Build succeeded: dist\fil2mid.exe
    popd
)
@echo off
SETLOCAL
set PY=.venv\Scripts\python.exe
if not exist %PY% (
  echo Python in venv not found at %PY%\nCreate or activate the venv first.
  exit /b 1
)
if exist requirements.txt (
  %PY% -m pip install -r requirements.txt
) else (
  %PY% -m pip install --upgrade pip setuptools wheel pyinstaller mido python-rtmidi
)
%PY% -m PyInstaller --onefile --name fil2mid --console tools\convert_fil_to_mid.py
if exist dist\fil2mid.exe (
  echo Built dist\fil2mid.exe
) else (
  echo Build failed. Check PyInstaller logs for details
  exit /b 1
)

@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (echo 请先运行 uv sync & pause & exit /b 1)
if not exist ui\dist\index.html (
  pushd ui
  call npm install
  if errorlevel 1 (popd & pause & exit /b 1)
  call npm run build
  if errorlevel 1 (popd & pause & exit /b 1)
  popd
)
echo 请在浏览器打开 http://localhost:18088 （端口可在.env.local中修改）
.venv\Scripts\python.exe run.py
pause

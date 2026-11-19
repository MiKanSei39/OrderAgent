@echo off
chcp 65001 >nul
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (echo 请先安装Node.js & pause & exit /b 1)
if not exist node_modules (call npm install || exit /b 1)
echo 前端地址：http://localhost:3000
echo 请先启动后端：http://localhost:18088
call npm run dev

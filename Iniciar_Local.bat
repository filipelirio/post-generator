@echo off
setlocal
title Easy Artigos - Inicializacao Local

echo ==========================================
echo   Iniciando Easy Artigos (LOCAL)
echo ==========================================
echo.

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "BACKEND_VENV_PY=%BACKEND_DIR%\venv\Scripts\python.exe"

if not exist "%BACKEND_DIR%\app\main.py" (
    echo [ERRO] Backend nao encontrado em "%BACKEND_DIR%".
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo [ERRO] Frontend nao encontrado em "%FRONTEND_DIR%".
    pause
    exit /b 1
)

echo [1/3] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js nao encontrado. Instale Node.js 18+.
    pause
    exit /b 1
)

echo [2/3] Verificando ambiente Python do backend...
if not exist "%BACKEND_VENV_PY%" (
    echo [ERRO] Ambiente virtual do backend nao encontrado em:
    echo         %BACKEND_VENV_PY%
    echo.
    echo Crie/preencha esse venv antes de usar o .bat.
    pause
    exit /b 1
)

echo [3/3] Iniciando servicos...

if not exist "%FRONTEND_DIR%\node_modules" (
    echo Instalando dependencias do frontend na primeira execucao...
    start "FRONTEND - npm install" cmd /k "cd /d "%FRONTEND_DIR%" && npm install"
    echo.
    echo Aguarde a instalacao do frontend terminar e execute o .bat novamente.
    pause
    exit /b 0
)

start "BACKEND - FastAPI" cmd /k "cd /d "%BACKEND_DIR%" && "%BACKEND_VENV_PY%" -m uvicorn app.main:app --host 0.0.0.0 --reload --port 8000 || pause"
start "FRONTEND - Next.js" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev || pause"

echo.
echo ==========================================
echo   Tudo pronto! Aguarde as janelas carregarem.
echo.
echo   - Backend:  http://localhost:8000/api/v1/docs
echo   - Frontend: http://localhost:3000
echo ==========================================
echo.
pause

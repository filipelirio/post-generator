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
set "BACKEND_PORT=8000"
set "FRONTEND_PORT="

for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command "$ports = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -ge 3000 -and $_.LocalPort -le 3005 } | Select-Object -ExpandProperty LocalPort -Unique | Sort-Object; [string]::Join(',', $ports)"`) do set "FRONTEND_PORTS_BEFORE=%%P"

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

for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command "$conn = Get-NetTCPConnection -State Listen -LocalPort %BACKEND_PORT% -ErrorAction SilentlyContinue | Select-Object -First 1; if ($conn) { $conn.OwningProcess }"`) do set "BACKEND_PID=%%P"

if defined BACKEND_PID (
    echo Porta %BACKEND_PORT% ja esta em uso pelo processo PID %BACKEND_PID%.
    for /f "usebackq delims=" %%C in (`powershell -NoProfile -Command "$p = Get-CimInstance Win32_Process -Filter \"ProcessId = %BACKEND_PID%\"; if ($p) { $p.CommandLine }"`) do set "BACKEND_CMD=%%C"

    echo Comando detectado:
    echo %BACKEND_CMD%
    echo.

    echo %BACKEND_CMD% | find /I "post-generator\\backend" >nul
    if %errorlevel% equ 0 (
        echo Instancia antiga do proprio backend detectada. Encerrando para reiniciar limpo...
        powershell -NoProfile -Command "Stop-Process -Id %BACKEND_PID% -Force"
        timeout /t 2 >nul
    ) else (
        echo [ERRO] A porta %BACKEND_PORT% esta ocupada por outro processo.
        echo Feche o processo acima ou altere manualmente a porta do backend.
        pause
        exit /b 1
    )
)

if not exist "%FRONTEND_DIR%\node_modules" (
    echo Instalando dependencias do frontend na primeira execucao...
    start "FRONTEND - npm install" cmd /k "cd /d "%FRONTEND_DIR%" && npm install"
    echo.
    echo Aguarde a instalacao do frontend terminar e execute o .bat novamente.
    pause
    exit /b 0
)

start "BACKEND - FastAPI" cmd /k "cd /d "%BACKEND_DIR%" && "%BACKEND_VENV_PY%" -m uvicorn app.main:app --host 127.0.0.1 --reload --port %BACKEND_PORT% || pause"
start "FRONTEND - Next.js" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev || pause"

for /L %%I in (1,1,20) do (
    for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command "$before = @('%FRONTEND_PORTS_BEFORE%'.Split(',') | Where-Object { $_ -ne '' } | ForEach-Object { [int]$_ }); $after = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -ge 3000 -and $_.LocalPort -le 3005 } | Select-Object -ExpandProperty LocalPort -Unique | Sort-Object; $newPort = $after | Where-Object { $before -notcontains $_ } | Select-Object -First 1; if ($newPort) { $newPort }"`) do set "FRONTEND_PORT=%%P"
    if defined FRONTEND_PORT goto :openBrowser
    timeout /t 1 >nul
)

goto :afterBrowser

:openBrowser
start "" "http://localhost:%FRONTEND_PORT%"

:afterBrowser

echo.
echo ==========================================
echo   Tudo pronto! Aguarde as janelas carregarem.
echo.
echo   - Backend:  http://localhost:%BACKEND_PORT%/api/v1/docs
if defined FRONTEND_PORT (
echo   - Frontend: http://localhost:%FRONTEND_PORT%
) else (
echo   - Frontend: porta nao detectada automaticamente
)
echo ==========================================
echo.
pause

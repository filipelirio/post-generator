@echo off
title Gerador de Artigos AI - Easy Evolução
echo ==========================================
echo   Iniciando Gerador de Artigos AI...
echo ==========================================
echo.

:: Verificar se o Docker está rodando
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] O Docker não parece estar rodando.
    echo Por favor, abra o Docker Desktop e tente novamente.
    pause
    exit /b
)

echo [1/2] Subindo containers (Backend + Frontend)...
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo [ERRO] Falha ao subir os containers.
    pause
    exit /b
)

echo.
echo [2/2] Tudo pronto! Acesse nos links abaixo:
echo.
echo 🌐 Frontend (Interface): http://localhost:3000
echo ⚙️  Backend (Documentação): http://localhost:8000/api/v1/docs
echo.
echo ==========================================
echo Pressione qualquer tecla para abrir o Gerador...
pause >nul
start http://localhost:3000
exit

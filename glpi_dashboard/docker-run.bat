@echo off
chcp 65001 >nul
REM Script para executar o projeto GLPI Dashboard com Docker no Windows

echo INICIANDO GLPI DASHBOARD COM DOCKER
echo ======================================

REM Verificar se Docker esta rodando
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Docker nao esta rodando. Por favor, inicie o Docker Desktop.
    pause
    exit /b 1
)

REM Parar containers existentes
echo [INFO] Parando containers existentes...
docker-compose down

REM Perguntar se quer remover imagens antigas
set /p remove_images="Remover imagens antigas? (y/N): "
if /i "%remove_images%"=="y" (
    echo [INFO] Removendo imagens antigas...
    docker-compose down --rmi all
)

REM Construir e iniciar os containers
echo [INFO] Construindo e iniciando containers...
docker-compose up --build -d

REM Aguardar os servicos ficarem prontos
echo [INFO] Aguardando servicos ficarem prontos...
timeout /t 10 /nobreak >nul

REM Verificar status dos containers
echo [INFO] Status dos containers:
docker-compose ps

REM Mostrar logs do backend
echo [INFO] Logs do backend:
docker-compose logs backend

echo.
echo PROJETO INICIADO COM SUCESSO!
echo ================================
echo Frontend: http://localhost:3001
echo Backend API: http://localhost:5000/api
echo MySQL: localhost:3307
echo Redis: localhost:6379
echo.
echo Comandos uteis:
echo   - Ver logs: docker-compose logs -f
echo   - Parar: docker-compose down
echo   - Reiniciar: docker-compose restart
echo   - Status: docker-compose ps
echo.
pause

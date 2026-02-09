@echo off
REM Script para rodar o bot com Podman/Docker no Windows

setlocal enabledelayedexpansion

echo ========================================
echo     Bot Mercado Livre - Runner
echo ========================================
echo.

REM Detecta se está usando Podman ou Docker
where podman >nul 2>&1
if %errorlevel% == 0 (
    set CONTAINER_CMD=podman
    set COMPOSE_CMD=podman-compose
    echo [OK] Podman detectado
) else (
    where docker >nul 2>&1
    if %errorlevel% == 0 (
        set CONTAINER_CMD=docker
        set COMPOSE_CMD=docker compose
        echo [OK] Docker detectado
    ) else (
        echo [ERRO] Nem Podman nem Docker foram encontrados
        echo.
        echo Instale um dos dois:
        echo   - Podman: https://podman.io/getting-started/installation
        echo   - Docker: https://docs.docker.com/get-docker/
        pause
        exit /b 1
    )
)

REM Verifica se o arquivo de credenciais existe
if not exist "account.txt" (
    echo [AVISO] Arquivo account.txt nao encontrado
    echo Criando arquivo de exemplo...
    (
        echo login = seu_email@exemplo.com
        echo password = sua_senha_segura
    ) > account.txt
    echo [OK] Arquivo account.txt criado
    echo [IMPORTANTE] Edite o arquivo account.txt com suas credenciais antes de continuar
    pause
    exit /b 1
)

REM Cria diretório de outputs se não existir
if not exist "outputs" mkdir outputs

echo.
echo Escolha uma opcao:
echo   1) Construir imagem
echo   2) Rodar bot (container unico)
echo   3) Rodar com compose
echo   4) Rodar testes
echo   5) Shell interativo
echo   6) Limpar containers/imagens
echo   7) Sair
echo.

set /p choice="Opcao: "

if "%choice%"=="1" goto build
if "%choice%"=="2" goto run_bot
if "%choice%"=="3" goto run_compose
if "%choice%"=="4" goto run_tests
if "%choice%"=="5" goto run_shell
if "%choice%"=="6" goto cleanup
if "%choice%"=="7" goto end
goto invalid

:build
echo.
echo [*] Construindo imagem...
%CONTAINER_CMD% build -t bot-mercadolivre:latest .
if %errorlevel% == 0 (
    echo [OK] Imagem construida com sucesso
) else (
    echo [ERRO] Falha ao construir imagem
    pause
    exit /b 1
)
if "%choice%"=="1" goto success
goto run_bot_exec

:run_bot
call :build
:run_bot_exec
echo.
echo [*] Iniciando bot...
%CONTAINER_CMD% run --rm --name bot-mercadolivre -e PYTHONUNBUFFERED=1 -e IN_DOCKER=true -e DISPLAY=:99 -v "%CD%\outputs:/app/outputs:z" -v "%CD%\account.txt:/app/account.txt:ro,z" bot-mercadolivre:latest
echo.
echo [OK] Bot finalizado
echo [INFO] Arquivos salvos em: .\outputs\
goto success

:run_compose
echo.
echo [*] Iniciando com %COMPOSE_CMD%...
%COMPOSE_CMD% up --build
echo.
echo [OK] Servico finalizado
goto success

:run_tests
call :build
echo.
echo [*] Executando testes...
%CONTAINER_CMD% run --rm --name bot-test -e PYTHONUNBUFFERED=1 -e IN_DOCKER=true -e DISPLAY=:99 -v "%CD%\account.txt:/app/account.txt:ro,z" bot-mercadolivre:latest python test_setup.py
echo.
echo [OK] Testes finalizados
goto success

:run_shell
call :build
echo.
echo [*] Abrindo shell interativo...
%CONTAINER_CMD% run --rm -it --name bot-shell -e PYTHONUNBUFFERED=1 -e IN_DOCKER=true -v "%CD%:/app:z" bot-mercadolivre:latest /bin/bash
goto success

:cleanup
echo.
echo [*] Limpando containers e imagens...
%CONTAINER_CMD% stop bot-mercadolivre 2>nul
%CONTAINER_CMD% rm bot-mercadolivre 2>nul
%CONTAINER_CMD% rmi bot-mercadolivre:latest 2>nul
echo [OK] Limpeza concluida
goto success

:invalid
echo [ERRO] Opcao invalida
pause
exit /b 1

:end
echo Ate logo!
exit /b 0

:success
echo.
echo ========================================
echo   Operacao concluida
echo ========================================
pause

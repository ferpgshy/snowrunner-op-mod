@echo off
chcp 65001 >nul
title SnowRunner OP Mod - Instalador
color 0A

echo ============================================================
echo   SNOWRUNNER OP MOD - INSTALADOR AUTOMATICO
echo ============================================================
echo.

:: Detectar pasta do script
set "SCRIPT_DIR=%~dp0"

:: Verificar se initial.pak existe na pasta
if not exist "%SCRIPT_DIR%initial.pak" (
    color 0C
    echo ERRO: initial.pak nao encontrado na pasta do instalador!
    echo Certifique-se de que todos os arquivos estao na mesma pasta.
    pause
    exit /b 1
)

:: Detectar pasta do jogo
set "GAME_DIR=C:\Program Files (x86)\Steam\steamapps\common\SnowRunner\preload\paks\client"
if not exist "%GAME_DIR%" (
    set "GAME_DIR=D:\SteamLibrary\steamapps\common\SnowRunner\preload\paks\client"
)
if not exist "%GAME_DIR%" (
    set "GAME_DIR=E:\SteamLibrary\steamapps\common\SnowRunner\preload\paks\client"
)
if not exist "%GAME_DIR%" (
    color 0E
    echo NAO ENCONTREI a pasta do SnowRunner automaticamente.
    echo.
    set /p "GAME_DIR=Cole o caminho da pasta client do jogo: "
)

if not exist "%GAME_DIR%" (
    color 0C
    echo ERRO: Pasta do jogo nao encontrada: %GAME_DIR%
    pause
    exit /b 1
)

:: Detectar pasta de mods (Documents\My Games\SnowRunner\base\Mods)
set "MODS_DIR=%USERPROFILE%\Documents\My Games\SnowRunner\base\Mods"
if not exist "%MODS_DIR%" (
    mkdir "%MODS_DIR%"
)

echo Pasta do jogo:  %GAME_DIR%
echo Pasta de mods:  %MODS_DIR%
echo.

:: Confirmar
echo Isso vai substituir o initial.pak e copiar os mods.
echo Feche o SnowRunner antes de continuar!
echo.
set /p "CONFIRM=Deseja continuar? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo Cancelado.
    pause
    exit /b 0
)

echo.
echo [1/2] Copiando initial.pak...
copy /y "%SCRIPT_DIR%initial.pak" "%GAME_DIR%\initial.pak"
if errorlevel 1 (
    color 0C
    echo ERRO ao copiar initial.pak! O jogo esta aberto?
    pause
    exit /b 1
)
echo       OK!

echo.
echo [2/2] Copiando mods (.modio)...
if exist "%SCRIPT_DIR%.modio" (
    xcopy "%SCRIPT_DIR%.modio" "%MODS_DIR%\.modio" /E /I /Y /Q
    if errorlevel 1 (
        color 0C
        echo ERRO ao copiar mods!
        pause
        exit /b 1
    )
    echo       OK!
) else (
    echo       Pasta .modio nao encontrada, pulando mods.
)

echo.
echo ============================================================
echo   INSTALACAO COMPLETA!
echo   Agora e so abrir o SnowRunner e aproveitar.
echo ============================================================
echo.
pause

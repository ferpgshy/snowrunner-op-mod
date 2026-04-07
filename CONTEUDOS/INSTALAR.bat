@echo off

:: ============================================================
:: Solicitar admin se nao tiver
:: ============================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

setlocal EnableDelayedExpansion
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

:: Detectar WinRAR
set "WINRAR=C:\Program Files\WinRAR\WinRAR.exe"
if not exist "%WINRAR%" set "WINRAR=C:\Program Files (x86)\WinRAR\WinRAR.exe"
if not exist "%WINRAR%" (
    color 0C
    echo ERRO: WinRAR nao encontrado! Instale o WinRAR para continuar.
    echo https://www.win-rar.com/download.html
    pause
    exit /b 1
)

:: ============================================================
:: Localizar pasta do jogo (Steam)
:: ============================================================
set "GAME_DIR="
for %%D in (C D E F G) do (
    if exist "%%D:\Program Files (x86)\Steam\steamapps\common\SnowRunner\preload\paks\client" (
        set "GAME_DIR=%%D:\Program Files (x86)\Steam\steamapps\common\SnowRunner\preload\paks\client"
    )
    if exist "%%D:\SteamLibrary\steamapps\common\SnowRunner\preload\paks\client" (
        set "GAME_DIR=%%D:\SteamLibrary\steamapps\common\SnowRunner\preload\paks\client"
    )
    if exist "%%D:\Steam\steamapps\common\SnowRunner\preload\paks\client" (
        set "GAME_DIR=%%D:\Steam\steamapps\common\SnowRunner\preload\paks\client"
    )
)

if not defined GAME_DIR (
    color 0E
    echo NAO ENCONTREI a pasta do SnowRunner automaticamente.
    echo.
    set /p "GAME_DIR=Cole o caminho da pasta client do jogo: "
)

if not exist "!GAME_DIR!" (
    color 0C
    echo ERRO: Pasta do jogo nao encontrada: !GAME_DIR!
    pause
    exit /b 1
)

:: ============================================================
:: Localizar pasta de mods (.modio)
:: ============================================================
set "MODS_DIR=%USERPROFILE%\Documents\My Games\SnowRunner\base\Mods\.modio\mods"

echo Pasta do jogo:  !GAME_DIR!
echo Pasta de mods:  !MODS_DIR!
echo.

:: Confirmar
echo Isso vai:
echo   1. Substituir o initial.pak do jogo
echo   2. Injetar XMLs modificados nos mods do modio (sem apagar nada)
echo.
echo Feche o SnowRunner antes de continuar!
echo.
set /p "CONFIRM=Deseja continuar? (S/N): "
if /i not "%CONFIRM%"=="S" (
    echo Cancelado.
    pause
    exit /b 0
)

:: ============================================================
:: PASSO 1: Substituir initial.pak
:: ============================================================
echo.
echo [1/2] Substituindo initial.pak...
copy /y "%SCRIPT_DIR%initial.pak" "!GAME_DIR!\initial.pak" >nul
if errorlevel 1 (
    color 0C
    echo ERRO ao copiar initial.pak! O jogo esta aberto?
    pause
    exit /b 1
)
echo       OK!

:: ============================================================
:: PASSO 2: Injetar XMLs nos .paks dos mods (WinRAR)
:: ============================================================
echo.
echo [2/2] Injetando XMLs nos mods...

if not exist "%SCRIPT_DIR%modio_patch" (
    echo       Pasta modio_patch nao encontrada, pulando mods.
    goto :done
)

if not exist "!MODS_DIR!" (
    color 0E
    echo       Pasta de mods nao encontrada: !MODS_DIR!
    echo       Pulando injecao de mods. Voce tem mods instalados pelo modio?
    goto :done
)

set "MOD_COUNT=0"
set "MOD_OK=0"
set "MOD_SKIP=0"

for /d %%M in ("%SCRIPT_DIR%modio_patch\*") do (
    set /a MOD_COUNT+=1
    for /d %%P in ("%%M\*") do (
        set "PAK_PATH=!MODS_DIR!\%%~nxM\%%~nxP.pak"
        if exist "!PAK_PATH!" (
            echo   [!MOD_COUNT!] Injetando em %%~nxP.pak...
            pushd "%%P"
            "!WINRAR!" a -afzip -o+ -r "!PAK_PATH!" * >nul
            popd
            if errorlevel 1 (
                echo          ERRO ao injetar!
            ) else (
                set /a MOD_OK+=1
            )
        ) else (
            set /a MOD_SKIP+=1
        )
    )
)

echo.
echo   Mods: !MOD_OK! injetados, !MOD_SKIP! pulados (nao instalados)

:done
echo.
echo ============================================================
echo   INSTALACAO COMPLETA!
echo   Agora e so abrir o SnowRunner e aproveitar.
echo ============================================================
echo.
pause

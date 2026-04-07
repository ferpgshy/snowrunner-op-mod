@echo off
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

:: Detectar pasta de mods
set "MODS_DIR=%USERPROFILE%\Documents\My Games\SnowRunner\base\Mods\.modio\mods"

echo Pasta do jogo:  %GAME_DIR%
echo Pasta de mods:  %MODS_DIR%
echo.

:: Confirmar
echo Isso vai instalar o initial.pak e injetar os mods nos seus .paks.
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
echo [2/2] Injetando mods nos .paks existentes...
if exist "%SCRIPT_DIR%modio_patch" (
    set "MOD_COUNT=0"
    set "MOD_OK=0"
    set "MOD_SKIP=0"
    for /d %%M in ("%SCRIPT_DIR%modio_patch\*") do (
        set /a MOD_COUNT+=1
        :: Pegar o mod_id (nome da pasta)
        set "MOD_ID=%%~nxM"
        :: Dentro de cada mod_id tem uma subpasta com o nome do pak
        for /d %%P in ("%%M\*") do (
            set "PAK_NAME=%%~nxP.pak"
            set "PAK_PATH=%MODS_DIR%\%%~nxM\%%~nxP.pak"
            if exist "!PAK_PATH!" (
                echo   Injetando em !PAK_NAME!...
                pushd "%%P"
                "%WINRAR%" a -afzip -o+ -r "!PAK_PATH!" *
                popd
                if errorlevel 1 (
                    echo     ERRO ao injetar!
                ) else (
                    set /a MOD_OK+=1
                )
            ) else (
                echo   %PAK_NAME% nao encontrado, pulando...
                set /a MOD_SKIP+=1
            )
        )
    )
    echo.
    echo   Mods injetados com sucesso!
) else (
    echo       Pasta modio_patch nao encontrada, pulando mods.
)

echo.
echo ============================================================
echo   INSTALACAO COMPLETA!
echo   Agora e so abrir o SnowRunner e aproveitar.
echo ============================================================
echo.
pause

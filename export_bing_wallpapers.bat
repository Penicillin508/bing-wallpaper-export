@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem ============================================================
rem Bing Wallpaper Export
rem Copy all extension-less files from the Spotlight assets folder
rem   %userprofile%\AppData\Local\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets
rem into %userprofile%\Downloads, renamed as BingWallpaper+YYMMDD+2-digit-seq+.jpg
rem
rem All paths use %userprofile% (resolved at runtime), so there is no
rem hard-coded username or drive letter. Works under any Windows user
rem or environment, e.g. C:\Users\someone or D:\Users\someone.
rem
rem Usage:
rem   export_bing_wallpapers.bat
rem   export_bing_wallpapers.bat "custom_source"
rem   export_bing_wallpapers.bat "custom_source" "custom_dest"
rem
rem NOTE: this file is intentionally ASCII-only. Non-ASCII (e.g. Chinese)
rem comments break cmd.exe on GBK-locale systems, so keep messages English.
rem Also avoid special chars like ">" inside echo lines within () blocks.
rem ============================================================

set "SRC=%userprofile%\AppData\Local\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets"
set "DST=%userprofile%\Downloads"
if not "%~1"=="" set "SRC=%~1"
if not "%~2"=="" set "DST=%~2"

rem --- Get date as YYMMDD: prefer wmic, fall back to PowerShell (locale independent) ---
set "YMD="
for /f "tokens=2 delims==." %%a in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%a"
if defined DT (
    set "YMD=!DT:~2,6!"
) else (
    for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format yyMMdd" 2^>nul') do set "YMD=%%a"
)
if not defined YMD (
    echo [ERROR] Cannot get current date.
    exit /b 1
)

rem --- Check source directory ---
if not exist "%SRC%\" (
    echo [ERROR] Source directory not found: %SRC%
    exit /b 1
)

rem --- Destination directory, create if missing ---
if not exist "%DST%\" mkdir "%DST%" >nul 2>&1

set "COPIED=0"
for /f "tokens=*" %%F in ('dir /b /a-d "%SRC%" 2^>nul') do (
    set "fext=%%~xF"
    if "!fext!"=="" (
        call :nextseq SEQSTR
        copy /b "%SRC%\%%F" "%DST%\BingWallpaper%YMD%!SEQSTR!.jpg" >nul
        if exist "%DST%\BingWallpaper%YMD%!SEQSTR!.jpg" (
            echo %%F  renamed to  BingWallpaper%YMD%!SEQSTR!.jpg
            set /a COPIED+=1
        ) else (
            echo [FAIL] %%F
        )
    )
)

echo.
if !COPIED! equ 0 (
    echo [DONE] No extension-less files in source, nothing to copy.
) else (
    echo [DONE] Copied !COPIED! file(s) into %DST%
)
exit /b 0

rem --- Subroutine: return next free 2-digit sequence, avoid overwriting existing files ---
:nextseq
set /a "n=1"
:seqloop
set "s=0%n%"
set "s=!s:~-2!"
if exist "%DST%\BingWallpaper%YMD%!s!.jpg" (
    set /a n+=1
    goto :seqloop
)
set "%~1=!s!"
goto :eof

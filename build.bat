@echo off
REM Скрипт сборки SubPlayer для Windows
REM Использование: build.bat [платформа]
REM Платформы: win, mac, linux, all (по умолчанию - текущая платформа)

setlocal enabledelayedexpansion

echo === SubPlayer Builder ===

REM Проверка наличия Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Node.js не установлен!
    echo Установите Node.js с https://nodejs.org/
    exit /b 1
)

REM Проверка наличия npm
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: npm не установлен!
    exit /b 1
)

node --version
npm --version

REM Определение платформы
set PLATFORM=%1
if "%PLATFORM%"=="" set PLATFORM=current

REM Установка зависимостей, если нужно
if not exist "node_modules" (
    echo Установка зависимостей...
    call npm install
) else (
    echo Зависимости уже установлены
)

REM Очистка предыдущих сборок
echo Очистка предыдущих сборок...
if exist "dist" rmdir /s /q "dist"

REM Сборка
echo Начало сборки для платформы: %PLATFORM%

if "%PLATFORM%"=="win" (
    echo Сборка для Windows...
    call npm run build:win
) else if "%PLATFORM%"=="mac" (
    echo Сборка для macOS...
    call npm run build:mac
) else if "%PLATFORM%"=="linux" (
    echo Сборка для Linux...
    call npm run build:linux
) else if "%PLATFORM%"=="all" (
    echo Сборка для всех платформ...
    call npm run build:all
) else (
    echo Сборка для текущей платформы...
    call npm run build
)

echo === Сборка завершена! ===
echo Результаты находятся в папке dist\

pause


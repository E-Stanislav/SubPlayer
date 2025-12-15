@echo off
REM Скрипт установки SubPlayer для Windows

echo ==========================================
echo   SubPlayer - Установка
echo ==========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python не найден. Установите Python 3.9 или выше.
    echo Скачайте с https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python найден:
python --version

REM Создание виртуального окружения
if not exist "venv" (
    echo.
    echo Создание виртуального окружения...
    python -m venv venv
    echo [OK] Виртуальное окружение создано
) else (
    echo [OK] Виртуальное окружение уже существует
)

REM Активация виртуального окружения
echo.
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Обновление pip
echo.
echo Обновление pip...
python -m pip install --upgrade pip setuptools wheel

REM Установка зависимостей
echo.
echo Установка зависимостей Python...
pip install -e .

REM Проверка системных зависимостей
echo.
echo Проверка системных зависимостей...

REM Проверка ffmpeg
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo [WARNING] ffmpeg не найден в PATH
    echo   Скачайте с https://ffmpeg.org/download.html
    echo   Или установите через chocolatey: choco install ffmpeg
) else (
    echo [OK] ffmpeg найден
    ffmpeg -version | findstr /C:"ffmpeg version"
)

REM Проверка mpv
where mpv >nul 2>&1
if errorlevel 1 (
    echo [WARNING] mpv не найден в PATH
    echo   Скачайте с https://mpv.io/installation/
    echo   Или установите через chocolatey: choco install mpv
    echo.
    echo   python-mpv может работать без системного mpv
) else (
    echo [OK] mpv найден
    mpv --version | findstr /C:"mpv"
)

echo.
echo ==========================================
echo   [OK] Установка завершена!
echo ==========================================
echo.
echo Для запуска приложения:
echo   venv\Scripts\activate
echo   python -m subplayer.app
echo.
echo Или используйте скрипт запуска:
echo   run.bat
echo.
pause


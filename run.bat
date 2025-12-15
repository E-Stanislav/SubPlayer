@echo off
REM Скрипт запуска SubPlayer для Windows

REM Проверка виртуального окружения
if not exist "venv" (
    echo [ERROR] Виртуальное окружение не найдено.
    echo Запустите сначала: setup.bat
    pause
    exit /b 1
)

REM Активация виртуального окружения и запуск
call venv\Scripts\activate.bat
python -m subplayer.app


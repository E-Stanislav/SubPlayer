@echo off
REM Скрипт установки зависимостей для SubPlayer (Windows)
REM Использование: install.bat

echo === Установка зависимостей SubPlayer ===

REM Проверка наличия Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Node.js не установлен!
    echo Установите Node.js с https://nodejs.org/
    pause
    exit /b 1
)

node --version
npm --version

echo Установка зависимостей...
call npm install

echo === Установка завершена! ===
echo Теперь вы можете запустить приложение командой: npm start
echo Или собрать приложение командой: build.bat

pause


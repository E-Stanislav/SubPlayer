#!/bin/bash
# Скрипт запуска SubPlayer для Linux/macOS

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено."
    echo "Запустите сначала: ./setup.sh"
    exit 1
fi

# Активация виртуального окружения и запуск
source venv/bin/activate
python -m subplayer.app


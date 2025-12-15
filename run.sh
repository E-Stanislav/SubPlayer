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

# Подавление предупреждений о конфликте libavdevice (не критично)
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

python -m subplayer.app


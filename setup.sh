#!/bin/bash
# Скрипт установки SubPlayer для Linux/macOS

set -e  # Остановка при ошибке

echo "=========================================="
echo "  SubPlayer - Установка"
echo "=========================================="
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.9 или выше."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "✓ Python найден: $(python3 --version)"

# Проверка версии Python
if [ "$(printf '%s\n' "3.9" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.9" ]; then
    echo "❌ Требуется Python 3.9 или выше. Найден: $PYTHON_VERSION"
    exit 1
fi

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo ""
    echo "Создание виртуального окружения..."
    python3 -m venv venv
    echo "✓ Виртуальное окружение создано"
else
    echo "✓ Виртуальное окружение уже существует"
fi

# Активация виртуального окружения
echo ""
echo "Активация виртуального окружения..."
source venv/bin/activate

# Обновление pip
echo ""
echo "Обновление pip..."
pip install --upgrade pip setuptools wheel

# Установка зависимостей
echo ""
echo "Установка зависимостей Python..."
pip install -e .

# Проверка системных зависимостей
echo ""
echo "Проверка системных зависимостей..."

# Проверка ffmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✓ ffmpeg найден: $(ffmpeg -version | head -n1)"
else
    echo "⚠ ffmpeg не найден в PATH"
    echo "  Установите ffmpeg:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "    brew install ffmpeg"
    else
        echo "    sudo apt install ffmpeg  # для Debian/Ubuntu"
        echo "    sudo yum install ffmpeg  # для CentOS/RHEL"
    fi
fi

# Проверка mpv
if command -v mpv &> /dev/null; then
    echo "✓ mpv найден: $(mpv --version | head -n1)"
else
    echo "⚠ mpv не найден в PATH"
    echo "  Установите mpv:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "    brew install mpv"
    else
        echo "    sudo apt install mpv  # для Debian/Ubuntu"
        echo "    sudo yum install mpv  # для CentOS/RHEL"
    fi
    echo ""
    echo "  Или установите python-mpv, который может работать без системного mpv"
fi

echo ""
echo "=========================================="
echo "  ✓ Установка завершена!"
echo "=========================================="
echo ""
echo "Для запуска приложения:"
echo "  source venv/bin/activate"
echo "  python -m subplayer.app"
echo ""
echo "Или используйте скрипт запуска:"
echo "  ./run.sh"
echo ""


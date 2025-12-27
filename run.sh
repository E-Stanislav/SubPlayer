#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "🎬 SubPlayer - Setup & Run"
echo "=========================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if command exists
check_cmd() {
    command -v "$1" &> /dev/null
}

# Check Node.js
if ! check_cmd node; then
    echo -e "${RED}❌ Node.js не установлен${NC}"
    echo "Установите: brew install node"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js $(node -v)"

# Check Python 3
if ! check_cmd python3; then
    echo -e "${RED}❌ Python3 не установлен${NC}"
    echo "Установите: brew install python3"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $(python3 --version | cut -d' ' -f2)"

# Check FFmpeg (optional but recommended)
if ! check_cmd ffmpeg; then
    echo -e "${YELLOW}⚠${NC} FFmpeg не установлен (рекомендуется для некоторых форматов)"
    echo "  Можно установить: brew install ffmpeg"
fi

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 Установка Node.js зависимостей..."
    npm install
else
    echo -e "${GREEN}✓${NC} Node.js зависимости установлены"
fi

# Setup Python venv if needed
if [ ! -d "python/venv" ]; then
    echo ""
    echo "🐍 Создание Python виртуального окружения..."
    python3 -m venv python/venv
fi

# Activate venv and check packages
source python/venv/bin/activate

# Check if base packages are installed
if ! python -c "import faster_whisper" 2>/dev/null; then
    echo ""
    echo "📦 Установка Python зависимостей..."
    pip install -q -r python/requirements.txt
else
    echo -e "${GREEN}✓${NC} Python зависимости установлены"
fi

# Check if TTS is installed (optional)
if python -c "import torch; torch.hub.list('snakers4/silero-models')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Silero TTS доступен"
else
    echo -e "${YELLOW}⚠${NC} Silero TTS будет загружен при первом использовании (~100 МБ)"
fi

deactivate

echo ""
echo "🔨 Сборка приложения..."
npx vite build 2>/dev/null

echo ""
echo "🚀 Запуск SubPlayer..."
echo ""
echo "Подсказки:"
echo "  • Включите 'Озвучка на русском' перед загрузкой видео для TTS"
echo "  • Нажмите T во время просмотра для переключения озвучки"
echo "  • Субтитры появляются по мере обработки — можно смотреть сразу"
echo ""

# Run in production mode (no dev tools, minimal logs)
npx electron . 2>/dev/null

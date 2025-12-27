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

# Check if Python packages are installed
source python/venv/bin/activate
if ! python -c "import faster_whisper" 2>/dev/null; then
    echo ""
    echo "📦 Установка Python зависимостей..."
    pip install -q -r python/requirements.txt
else
    echo -e "${GREEN}✓${NC} Python зависимости установлены"
fi
deactivate

# Build if needed
if [ ! -d "dist" ] || [ ! -d "dist-electron" ]; then
    echo ""
    echo "🔨 Сборка приложения..."
    npm run build 2>/dev/null || {
        # If build script doesn't exist, use vite directly
        npx vite build
    }
fi

# Check if app exists
APP_PATH="release/mac-arm64/SubPlayer.app"
if [ ! -d "$APP_PATH" ]; then
    echo ""
    echo "📦 Сборка Electron приложения..."
    npm run electron:build 2>/dev/null || {
        npx vite build && npx electron-builder --mac --arm64
    }
fi

echo ""
echo "🚀 Запуск SubPlayer..."
echo ""

# Run the app
if [ -d "$APP_PATH" ]; then
    open "$APP_PATH"
else
    # Fallback: run in dev mode
    echo "Запуск в режиме разработки..."
    npm run dev
fi


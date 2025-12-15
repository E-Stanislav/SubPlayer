#!/bin/bash

# Скрипт сборки SubPlayer для Unix-систем (macOS/Linux)
# Использование: ./build.sh [платформа]
# Платформы: win, mac, linux, all (по умолчанию - текущая платформа)

set -e  # Остановка при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== SubPlayer Builder ===${NC}"

# Проверка наличия Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Ошибка: Node.js не установлен!${NC}"
    echo "Установите Node.js с https://nodejs.org/"
    exit 1
fi

# Проверка наличия npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Ошибка: npm не установлен!${NC}"
    exit 1
fi

echo -e "${YELLOW}Версия Node.js: $(node --version)${NC}"
echo -e "${YELLOW}Версия npm: $(npm --version)${NC}"

# Определение платформы
PLATFORM=${1:-current}

# Установка зависимостей, если нужно
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Установка зависимостей...${NC}"
    npm install
else
    echo -e "${GREEN}Зависимости уже установлены${NC}"
fi

# Очистка предыдущих сборок
echo -e "${YELLOW}Очистка предыдущих сборок...${NC}"
rm -rf dist

# Сборка
echo -e "${GREEN}Начало сборки для платформы: ${PLATFORM}${NC}"

case $PLATFORM in
    win)
        echo -e "${YELLOW}Сборка для Windows...${NC}"
        npm run build:win
        ;;
    mac)
        echo -e "${YELLOW}Сборка для macOS...${NC}"
        npm run build:mac
        ;;
    linux)
        echo -e "${YELLOW}Сборка для Linux...${NC}"
        npm run build:linux
        ;;
    all)
        echo -e "${YELLOW}Сборка для всех платформ...${NC}"
        npm run build:all
        ;;
    current|*)
        echo -e "${YELLOW}Сборка для текущей платформы...${NC}"
        npm run build
        ;;
esac

echo -e "${GREEN}=== Сборка завершена! ===${NC}"
echo -e "${GREEN}Результаты находятся в папке dist/${NC}"

# Показать размер результатов
if [ -d "dist" ]; then
    echo -e "${YELLOW}Размер результатов:${NC}"
    du -sh dist/*
fi


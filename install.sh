#!/bin/bash

# Скрипт установки зависимостей для SubPlayer
# Использование: ./install.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Установка зависимостей SubPlayer ===${NC}"

# Проверка наличия Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}Ошибка: Node.js не установлен!${NC}"
    echo "Установите Node.js с https://nodejs.org/"
    exit 1
fi

echo -e "${YELLOW}Версия Node.js: $(node --version)${NC}"
echo -e "${YELLOW}Версия npm: $(npm --version)${NC}"

echo -e "${YELLOW}Установка зависимостей...${NC}"
npm install

echo -e "${GREEN}=== Установка завершена! ===${NC}"
echo -e "${GREEN}Теперь вы можете запустить приложение командой: npm start${NC}"
echo -e "${GREEN}Или собрать приложение командой: ./build.sh${NC}"


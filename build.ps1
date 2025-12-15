# Скрипт сборки SubPlayer для Windows (PowerShell)
# Использование: .\build.ps1 [платформа]
# Платформы: win, mac, linux, all (по умолчанию - текущая платформа)

$ErrorActionPreference = "Stop"

Write-Host "=== SubPlayer Builder ===" -ForegroundColor Green

# Проверка наличия Node.js
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "Версия Node.js: $nodeVersion" -ForegroundColor Yellow
    Write-Host "Версия npm: $npmVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Ошибка: Node.js не установлен!" -ForegroundColor Red
    Write-Host "Установите Node.js с https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Определение платформы
$platform = if ($args.Count -gt 0) { $args[0] } else { "current" }

# Установка зависимостей, если нужно
if (-not (Test-Path "node_modules")) {
    Write-Host "Установка зависимостей..." -ForegroundColor Yellow
    npm install
} else {
    Write-Host "Зависимости уже установлены" -ForegroundColor Green
}

# Очистка предыдущих сборок
Write-Host "Очистка предыдущих сборок..." -ForegroundColor Yellow
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}

# Сборка
Write-Host "Начало сборки для платформы: $platform" -ForegroundColor Green

switch ($platform) {
    "win" {
        Write-Host "Сборка для Windows..." -ForegroundColor Yellow
        npm run build:win
    }
    "mac" {
        Write-Host "Сборка для macOS..." -ForegroundColor Yellow
        npm run build:mac
    }
    "linux" {
        Write-Host "Сборка для Linux..." -ForegroundColor Yellow
        npm run build:linux
    }
    "all" {
        Write-Host "Сборка для всех платформ..." -ForegroundColor Yellow
        npm run build:all
    }
    default {
        Write-Host "Сборка для текущей платформы..." -ForegroundColor Yellow
        npm run build
    }
}

Write-Host "=== Сборка завершена! ===" -ForegroundColor Green
Write-Host "Результаты находятся в папке dist\" -ForegroundColor Green

# Показать размер результатов
if (Test-Path "dist") {
    Write-Host "`nРазмер результатов:" -ForegroundColor Yellow
    Get-ChildItem "dist" | ForEach-Object {
        $size = (Get-ChildItem $_.FullName -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "  $($_.Name): $([math]::Round($size, 2)) MB"
    }
}

Read-Host "Нажмите Enter для выхода"


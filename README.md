# SubPlayer

Видеопроигрыватель с автоматическим созданием субтитров и переводом на русский язык.

## Возможности

- Автоматическое распознавание речи через **Faster Whisper** (до 4x быстрее оригинального Whisper)
- Перевод субтитров на русский язык через **Argos Translate** (полностью локально)
- Поддержка всех популярных видеоформатов (MP4, MKV, AVI, MOV, WebM)
- Красивый современный интерфейс
- Полностью офлайн работа после загрузки моделей

## Системные требования

- macOS 10.15+ / Windows 10+ / Linux
- Python 3.9+
- FFmpeg (`brew install ffmpeg` на macOS)
- 4+ ГБ RAM (рекомендуется 8+ ГБ для больших моделей)

## Установка

### 1. Клонирование и установка Node.js зависимостей

```bash
cd SubPlayer
npm install
```

### 2. Установка Python зависимостей

```bash
cd python
pip install -r requirements.txt
```

Или создайте виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate  # на macOS/Linux
pip install -r requirements.txt
```

### 3. Установка FFmpeg (если не установлен)

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

## Запуск

### Режим разработки

```bash
npm run dev
```

### Сборка приложения

```bash
npm run electron:build
```

## Модели Whisper

При первом запуске автоматически загрузится модель `base` (~150 МБ). 
Доступные модели:

| Модель | Размер | RAM | Скорость | Качество |
|--------|--------|-----|----------|----------|
| tiny | ~75 МБ | ~1 ГБ | Очень быстро | Базовое |
| base | ~150 МБ | ~1 ГБ | Быстро | Хорошее |
| small | ~500 МБ | ~2 ГБ | Средне | Очень хорошее |
| medium | ~1.5 ГБ | ~5 ГБ | Медленно | Отличное |
| large-v3 | ~3 ГБ | ~10 ГБ | Очень медленно | Наилучшее |

Для изменения модели отредактируйте `DEFAULT_MODEL` в `python/transcribe.py`.

## Горячие клавиши

| Клавиша | Действие |
|---------|----------|
| `Space` | Пауза/Воспроизведение |
| `←` / `→` | Перемотка ±5 сек |
| `↑` / `↓` | Громкость ±10% |
| `M` | Без звука |
| `F` | Полный экран |

## Структура проекта

```
SubPlayer/
├── electron/           # Electron main process
│   ├── main.ts
│   ├── preload.ts
│   └── python-bridge.ts
├── src/               # React frontend
│   ├── components/
│   ├── hooks/
│   └── styles/
├── python/            # Python backend
│   ├── process.py
│   ├── transcribe.py
│   └── translate.py
└── package.json
```

## Лицензия

MIT


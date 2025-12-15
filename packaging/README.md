# Инструкции по сборке portable версии SubPlayer

## Требования

- Python 3.9+
- PyInstaller
- Все зависимости из `pyproject.toml`

## Подготовка

1. Установите зависимости:
   ```bash
   pip install -e .
   pip install pyinstaller
   ```

2. Подготовьте бинарные файлы согласно инструкциям:
   - `../tools/bundle_mpv.md` - mpv/libmpv
   - `../tools/bundle_ffmpeg.md` - ffmpeg
   - `../tools/bundle_fasterwhisper.md` - faster-whisper (опционально, модели)

3. Поместите бинарные файлы в соответствующие папки:
   ```
   packaging/
   ├── binaries/
   │   ├── windows/
   │   │   ├── mpv-1.dll
   │   │   └── ffmpeg.exe
   │   ├── macos/
   │   │   ├── libmpv.dylib
   │   │   └── ffmpeg
   │   └── linux/
   │       ├── libmpv.so
   │       └── ffmpeg
   └── models/  (опционально, для включения моделей в сборку)
       └── ...
   ```

**Примечание**: faster-whisper - это Python библиотека, она автоматически включается в сборку. Модели Whisper скачиваются автоматически при первом использовании, но вы можете включить их в сборку для полностью офлайн версии.

## Сборка

### Windows

```bash
pyinstaller packaging/pyinstaller.spec
```

Результат будет в `dist/SubPlayer/` - это portable папка со всеми файлами.

### macOS

```bash
pyinstaller packaging/pyinstaller.spec
```

Результат будет в `dist/SubPlayer.app` - это macOS приложение.

### Linux

```bash
pyinstaller packaging/pyinstaller.spec
```

Результат будет в `dist/SubPlayer/` - это portable папка.

## Обновление pyinstaller.spec

После добавления бинарных файлов обновите `pyinstaller.spec`:

```python
binaries=[
    ('packaging/binaries/windows/mpv-1.dll', '.'),
    ('packaging/binaries/windows/ffmpeg.exe', '.'),
],

# Опционально: включить модели Whisper
datas=[
    ('packaging/models', 'models'),
],
```

## Примечания

- Убедитесь, что все пути к бинарным файлам правильные
- Проверьте, что все зависимости включены
- Для Linux рассмотрите создание AppImage для лучшей портативности
- Для macOS может потребоваться подписание приложения для распространения


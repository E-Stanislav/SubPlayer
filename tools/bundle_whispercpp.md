# Инструкция по включению whisper.cpp в сборку

## Windows

1. Скачайте скомпилированный `whisper.exe` с [релизов whisper.cpp](https://github.com/ggerganov/whisper.cpp/releases)
2. Поместите `whisper.exe` в папку `packaging/binaries/windows/`
3. В `pyinstaller.spec` добавьте в `binaries`:
   ```python
   binaries=[('packaging/binaries/windows/whisper.exe', '.')],
   ```

## macOS

1. Скомпилируйте whisper.cpp:
   ```bash
   git clone https://github.com/ggerganov/whisper.cpp
   cd whisper.cpp
   make
   ```
2. Скопируйте `main` в `packaging/binaries/macos/whisper`
3. В `pyinstaller.spec` добавьте в `binaries`:
   ```python
   binaries=[('packaging/binaries/macos/whisper', '.')],
   ```

## Linux

1. Скомпилируйте whisper.cpp:
   ```bash
   git clone https://github.com/ggerganov/whisper.cpp
   cd whisper.cpp
   make
   ```
2. Скопируйте `main` в `packaging/binaries/linux/whisper`
3. В `pyinstaller.spec` добавьте в `binaries`:
   ```python
   binaries=[('packaging/binaries/linux/whisper', '.')],
   ```

## Модели Whisper

Модели нужно скачать отдельно и включить в сборку:

1. Скачайте модели с [Hugging Face](https://huggingface.co/ggerganov/whisper.cpp) или используйте скрипт:
   ```bash
   # Пример для модели base
   wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
   ```

2. Поместите модели в `packaging/models/`

3. В `pyinstaller.spec` добавьте в `datas`:
   ```python
   datas=[('packaging/models', 'models')],
   ```

4. Обновите код для поиска моделей в папке приложения


# Инструкция по включению ffmpeg в сборку

## Windows

1. Скачайте ffmpeg для Windows с [официального сайта](https://ffmpeg.org/download.html) или используйте [статические сборки](https://www.gyan.dev/ffmpeg/builds/)
2. Извлеките `ffmpeg.exe` из архива
3. Поместите `ffmpeg.exe` в папку `packaging/binaries/windows/`
4. В `pyinstaller.spec` добавьте в `binaries`:
   ```python
   binaries=[('packaging/binaries/windows/ffmpeg.exe', '.')],
   ```

## macOS

1. Установите ffmpeg через Homebrew:
   ```bash
   brew install ffmpeg
   ```

2. Найдите исполняемый файл:
   ```bash
   which ffmpeg
   # Обычно: /opt/homebrew/bin/ffmpeg
   ```

3. Скопируйте `ffmpeg` в `packaging/binaries/macos/`

4. В `pyinstaller.spec` добавьте в `binaries`:
   ```python
   binaries=[('packaging/binaries/macos/ffmpeg', '.')],
   ```

### Альтернатива: Статическая сборка

Для portable версии можно собрать статический ffmpeg.

## Linux

1. Установите ffmpeg через пакетный менеджер:
   ```bash
   sudo apt install ffmpeg  # Debian/Ubuntu
   sudo yum install ffmpeg  # CentOS/RHEL
   ```

2. Найдите исполняемый файл:
   ```bash
   which ffmpeg
   # Обычно: /usr/bin/ffmpeg
   ```

3. Скопируйте `ffmpeg` в `packaging/binaries/linux/`

4. В `pyinstaller.spec` добавьте в `binaries`:
   ```python
   binaries=[('packaging/binaries/linux/ffmpeg', '.')],
   ```

## Примечания

- На Linux может потребоваться также включить зависимости ffmpeg
- Для portable версии убедитесь, что все зависимости включены
- Можно использовать статические сборки ffmpeg для полной портативности


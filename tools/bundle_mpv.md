# Инструкция по включению mpv/libmpv в сборку

## Windows

### Вариант 1: Использование python-mpv (рекомендуется)

`python-mpv` автоматически ищет `mpv-1.dll` в системных путях или рядом с приложением.

1. Скачайте mpv для Windows с [официального сайта](https://mpv.io/installation/)
2. Извлеките `mpv-1.dll` из архива
3. Поместите `mpv-1.dll` в папку `packaging/binaries/windows/`
4. В `pyinstaller.spec` добавьте в `binaries`:
   ```python
   binaries=[('packaging/binaries/windows/mpv-1.dll', '.')],
   ```

### Вариант 2: Статическая сборка

Для полностью portable версии можно собрать статическую версию mpv, но это сложнее.

## macOS

### Использование Homebrew

1. Установите mpv через Homebrew:
   ```bash
   brew install mpv
   ```

2. Найдите библиотеку:
   ```bash
   brew --prefix mpv
   # Обычно: /opt/homebrew/lib/libmpv.dylib
   ```

3. Скопируйте `libmpv.dylib` в `packaging/binaries/macos/`

4. В `pyinstaller.spec` добавьте в `binaries`:
   ```python
   binaries=[('packaging/binaries/macos/libmpv.dylib', '.')],
   ```

### Альтернатива: Сборка из исходников

Для полностью portable версии нужно собрать mpv статически.

## Linux

### Использование системных библиотек

1. Установите mpv через пакетный менеджер:
   ```bash
   sudo apt install mpv  # Debian/Ubuntu
   sudo yum install mpv  # CentOS/RHEL
   ```

2. Найдите библиотеку:
   ```bash
   find /usr -name "libmpv.so*" 2>/dev/null
   ```

3. Скопируйте `libmpv.so` в `packaging/binaries/linux/`

4. В `pyinstaller.spec` добавьте в `binaries`:
   ```python
   binaries=[('packaging/binaries/linux/libmpv.so', '.')],
   ```

### Альтернатива: AppImage

Для Linux можно создать AppImage, который включает все зависимости.

## Примечания

- На Linux и macOS может потребоваться также включить зависимости mpv (ffmpeg, etc.)
- Для полностью portable версии рассмотрите использование AppImage (Linux) или DMG (macOS)
- На Windows можно использовать NSIS или Inno Setup для создания установщика


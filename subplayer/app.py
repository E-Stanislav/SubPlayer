"""Точка входа приложения SubPlayer"""
import sys
import locale
import os

# Установка C локали для предотвращения проблем с mpv и другими библиотеками
try:
    locale.setlocale(locale.LC_NUMERIC, 'C')
except locale.Error:
    # Если C локаль недоступна, пробуем en_US.UTF-8
    try:
        locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')
    except locale.Error:
        pass

# Установка переменных окружения для предотвращения конфликтов
os.environ.setdefault('LC_NUMERIC', 'C')

from PySide6.QtWidgets import QApplication
from subplayer.ui.main_window import MainWindow


def main():
    """Главная функция запуска приложения"""
    app = QApplication(sys.argv)
    app.setApplicationName("SubPlayer")
    app.setOrganizationName("SubPlayer")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


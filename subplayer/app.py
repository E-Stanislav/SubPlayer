"""Точка входа приложения SubPlayer"""
import sys
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


"""Виджет для встраивания mpv в Qt"""
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
import platform


class MPVWidget(QWidget):
    """Виджет для отображения mpv плеера"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DontCreateNativeAncestors)
        self.setAttribute(Qt.WA_NativeWindow)
        self._widget_id = None
    
    def get_widget_id(self) -> int:
        """Получить native window ID для mpv"""
        if self._widget_id is None:
            # Получаем native window ID
            if platform.system() == "Windows":
                self._widget_id = int(self.winId())
            elif platform.system() == "Darwin":  # macOS
                # На macOS нужно использовать NSView
                from PySide6.QtGui import QWindow
                window = self.window().windowHandle()
                if window:
                    self._widget_id = int(window.winId())
                else:
                    self._widget_id = int(self.winId())
            else:  # Linux
                self._widget_id = int(self.winId())
        return self._widget_id
    
    def showEvent(self, event):
        """Обработка события показа виджета"""
        super().showEvent(event)
        # Убеждаемся, что виджет создан
        self.get_widget_id()


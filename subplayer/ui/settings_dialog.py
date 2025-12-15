"""Диалог настроек"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QLineEdit, QFileDialog, QGroupBox,
    QFormLayout, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt
from subplayer.util.settings import Settings
from pathlib import Path


class SettingsDialog(QDialog):
    """Диалог настроек приложения"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(500)
        
        self.settings = Settings()
        
        # Главный layout
        main_layout = QVBoxLayout(self)
        
        # Whisper настройки
        whisper_group = QGroupBox("Whisper (генерация субтитров)")
        whisper_layout = QFormLayout(whisper_group)
        
        # Модель
        self.model_combo = QComboBox()
        self.model_combo.addItems(['tiny', 'base', 'small', 'medium', 'large-v2', 'large-v3'])
        self.model_combo.setCurrentText(self.settings.get_whisper_model())
        whisper_layout.addRow("Модель:", self.model_combo)
        
        # Язык
        self.language_combo = QComboBox()
        self.language_combo.addItem("Автоопределение", None)
        self.language_combo.addItems(['en', 'ru', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'zh'])
        current_lang = self.settings.get_whisper_language()
        if current_lang:
            index = self.language_combo.findData(current_lang)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
        whisper_layout.addRow("Язык:", self.language_combo)
        
        # Устройство
        self.device_combo = QComboBox()
        self.device_combo.addItems(['auto', 'cpu', 'cuda'])
        device = self.settings.get('whisper', 'device', 'auto')
        self.device_combo.setCurrentText(device)
        whisper_layout.addRow("Устройство:", self.device_combo)
        
        # Тип вычислений
        self.compute_type_combo = QComboBox()
        self.compute_type_combo.addItems(['default', 'int8', 'int8_float16', 'int16', 'float16'])
        compute_type = self.settings.get('whisper', 'compute_type', 'default')
        self.compute_type_combo.setCurrentText(compute_type)
        whisper_layout.addRow("Тип вычислений:", self.compute_type_combo)
        
        # Путь к модели (опционально, для локальных моделей)
        model_path_layout = QHBoxLayout()
        self.model_path_edit = QLineEdit()
        model_path_value = self.settings.get('whisper', 'model_path')
        if model_path_value:
            self.model_path_edit.setText(model_path_value)
        self.model_path_edit.setPlaceholderText("Авто (скачивается автоматически)")
        model_path_btn = QPushButton("Обзор...")
        model_path_btn.clicked.connect(self._browse_model_path)
        model_path_layout.addWidget(self.model_path_edit)
        model_path_layout.addWidget(model_path_btn)
        whisper_layout.addRow("Путь к модели (опционально):", model_path_layout)
        
        main_layout.addWidget(whisper_group)
        
        # Перевод настройки
        translation_group = QGroupBox("Перевод")
        translation_layout = QFormLayout(translation_group)
        
        # Целевой язык
        self.target_lang_combo = QComboBox()
        self.target_lang_combo.addItems(['ru', 'en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'ko', 'zh'])
        self.target_lang_combo.setCurrentText(self.settings.get_translation_target_language())
        translation_layout.addRow("Целевой язык:", self.target_lang_combo)
        
        main_layout.addWidget(translation_group)
        
        # Кэш настройки
        cache_group = QGroupBox("Кэш")
        cache_layout = QFormLayout(cache_group)
        
        self.cache_enabled_check = QCheckBox("Включить кэширование")
        self.cache_enabled_check.setChecked(self.settings.get('cache', 'enabled', True))
        cache_layout.addRow(self.cache_enabled_check)
        
        main_layout.addWidget(cache_group)
        
        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._save_and_close)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
    
    def _browse_model_path(self):
        """Выбрать путь к модели"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите модель Whisper",
            "",
            "Модели (*.bin);;Все файлы (*)"
        )
        if path:
            self.model_path_edit.setText(path)
    
    def _save_and_close(self):
        """Сохранить настройки и закрыть"""
        try:
            # Сохраняем настройки Whisper
            self.settings.set_whisper_model(self.model_combo.currentText())
            
            language = self.language_combo.currentData()
            self.settings.set_whisper_language(language)
            
            self.settings.set('whisper', 'device', self.device_combo.currentText())
            self.settings.set('whisper', 'compute_type', self.compute_type_combo.currentText())
            
            model_path = self.model_path_edit.text().strip()
            if model_path:
                self.settings.set('whisper', 'model_path', model_path)
            else:
                self.settings.set('whisper', 'model_path', None)
            
            # Сохраняем настройки перевода
            self.settings.set_translation_target_language(self.target_lang_combo.currentText())
            
            # Сохраняем настройки кэша
            self.settings.set('cache', 'enabled', self.cache_enabled_check.isChecked())
            
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения настроек: {str(e)}")


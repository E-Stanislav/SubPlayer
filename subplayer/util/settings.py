"""Настройки приложения"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
from subplayer.util.paths import get_app_data_dir


class Settings:
    """Класс для управления настройками"""
    
    def __init__(self, settings_file: Optional[Path] = None):
        """
        Инициализация настроек
        
        Args:
            settings_file: путь к файлу настроек (если None, используется стандартный)
        """
        self.settings_file = settings_file or (get_app_data_dir() / "settings.json")
        self._settings = self._load_settings()
        self._apply_defaults()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Загрузить настройки из файла"""
        if self.settings_file.exists():
            try:
                return json.loads(self.settings_file.read_text(encoding='utf-8'))
            except:
                return {}
        return {}
    
    def _apply_defaults(self):
        """Применить настройки по умолчанию"""
        defaults = {
            'whisper': {
                'model': 'base',
                'language': None,  # автоопределение
                'model_path': None,  # автоопределение (скачивается автоматически)
                'device': 'auto',  # 'auto', 'cpu', 'cuda'
                'compute_type': 'default',  # 'default', 'int8', 'int8_float16', 'int16', 'float16'
            },
            'translation': {
                'target_language': 'ru',
                'auto_detect_source': True,
            },
            'cache': {
                'enabled': True,
                'cache_dir': None,  # стандартная директория
            },
            'paths': {
                'ffmpeg_path': None,  # автоопределение
            },
            'ui': {
                'window_geometry': None,
                'window_state': None,
            }
        }
        
        # Применяем значения по умолчанию только если их нет
        for category, values in defaults.items():
            if category not in self._settings:
                self._settings[category] = values
            else:
                for key, value in values.items():
                    if key not in self._settings[category]:
                        self._settings[category][key] = value
    
    def save(self):
        """Сохранить настройки в файл"""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            self.settings_file.write_text(
                json.dumps(self._settings, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def get(self, category: str, key: str, default: Any = None) -> Any:
        """Получить значение настройки"""
        return self._settings.get(category, {}).get(key, default)
    
    def set(self, category: str, key: str, value: Any):
        """Установить значение настройки"""
        if category not in self._settings:
            self._settings[category] = {}
        self._settings[category][key] = value
        self.save()
    
    def get_whisper_model(self) -> str:
        """Получить модель Whisper"""
        return self.get('whisper', 'model', 'base')
    
    def set_whisper_model(self, model: str):
        """Установить модель Whisper"""
        self.set('whisper', 'model', model)
    
    def get_whisper_language(self) -> Optional[str]:
        """Получить язык для Whisper (None = автоопределение)"""
        return self.get('whisper', 'language', None)
    
    def set_whisper_language(self, language: Optional[str]):
        """Установить язык для Whisper"""
        self.set('whisper', 'language', language)
    
    def get_translation_target_language(self) -> str:
        """Получить целевой язык перевода"""
        return self.get('translation', 'target_language', 'ru')
    
    def set_translation_target_language(self, language: str):
        """Установить целевой язык перевода"""
        self.set('translation', 'target_language', language)


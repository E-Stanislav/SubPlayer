"""Перевод субтитров через Argos Translate"""
from pathlib import Path
from typing import Optional, List
import argostranslate.package
import argostranslate.translate
from subplayer.subs.srt import SubtitleSegment, parse_srt_file, write_srt_file, get_srt_path_for_media


class ArgosTranslator:
    """Класс для перевода субтитров через Argos Translate"""
    
    def __init__(self):
        """Инициализация переводчика"""
        self._installed_packages = None
        self._update_installed_packages()
    
    def _update_installed_packages(self):
        """Обновить список установленных языковых пакетов"""
        argostranslate.package.update_package_index()
        self._installed_packages = argostranslate.package.get_installed_packages()
    
    def get_installed_languages(self) -> List[str]:
        """Получить список установленных языков"""
        languages = set()
        for package in self._installed_packages:
            languages.add(package.from_code)
            languages.add(package.to_code)
        return sorted(list(languages))
    
    def is_translation_available(self, from_lang: str, to_lang: str) -> bool:
        """Проверить, доступен ли перевод между языками"""
        for package in self._installed_packages:
            if package.from_code == from_lang and package.to_code == to_lang:
                return True
        return False
    
    def install_language_package(self, from_lang: str, to_lang: str) -> bool:
        """
        Установить языковой пакет
        
        Args:
            from_lang: исходный язык (код ISO 639-1)
            to_lang: целевой язык (код ISO 639-1)
        
        Returns:
            True если успешно установлен
        """
        try:
            # Обновляем индекс пакетов
            argostranslate.package.update_package_index()
            
            # Ищем нужный пакет
            available_packages = argostranslate.package.get_available_packages()
            package_to_install = None
            
            for package in available_packages:
                if package.from_code == from_lang and package.to_code == to_lang:
                    package_to_install = package
                    break
            
            if package_to_install is None:
                return False
            
            # Устанавливаем пакет
            argostranslate.package.install_from_path(package_to_install.download())
            
            # Обновляем список установленных пакетов
            self._update_installed_packages()
            
            return True
        except Exception as e:
            print(f"Ошибка установки языкового пакета: {e}")
            return False
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Определить язык текста (простая эвристика)
        
        Args:
            text: текст для определения языка
        
        Returns:
            Код языка или None
        """
        # Простая эвристика: проверяем наличие кириллицы
        if any('\u0400' <= char <= '\u04FF' for char in text):
            return 'ru'
        
        # Проверяем наличие латиницы (скорее всего английский)
        if any(char.isalpha() and ord(char) < 128 for char in text):
            return 'en'
        
        # По умолчанию английский
        return 'en'
    
    def translate_text(self, text: str, from_lang: str, to_lang: str) -> str:
        """
        Перевести текст
        
        Args:
            text: текст для перевода
            from_lang: исходный язык
            to_lang: целевой язык
        
        Returns:
            Переведённый текст
        """
        if from_lang == to_lang:
            return text
        
        if not self.is_translation_available(from_lang, to_lang):
            raise RuntimeError(
                f"Перевод {from_lang} -> {to_lang} недоступен. "
                f"Установите языковой пакет."
            )
        
        return argostranslate.translate.translate(text, from_lang, to_lang)
    
    def translate_subtitle_segment(
        self,
        segment: SubtitleSegment,
        from_lang: str,
        to_lang: str
    ) -> SubtitleSegment:
        """
        Перевести сегмент субтитров
        
        Args:
            segment: сегмент субтитров
            from_lang: исходный язык
            to_lang: целевой язык
        
        Returns:
            Переведённый сегмент
        """
        translated_text = self.translate_text(segment.text, from_lang, to_lang)
        return SubtitleSegment(
            segment.index,
            segment.start_time,
            segment.end_time,
            translated_text
        )
    
    def translate_srt_file(
        self,
        srt_path: Path,
        output_path: Optional[Path] = None,
        from_lang: Optional[str] = None,
        to_lang: str = "ru",
        progress_callback: Optional[callable] = None
    ) -> Path:
        """
        Перевести SRT файл
        
        Args:
            srt_path: путь к исходному SRT файлу
            output_path: путь для сохранения переведённого файла (если None, создаётся рядом)
            from_lang: исходный язык (если None, определяется автоматически)
            to_lang: целевой язык (по умолчанию 'ru')
            progress_callback: функция для обновления прогресса (сообщение, прогресс 0-100)
        
        Returns:
            Путь к переведённому SRT файлу
        """
        if not srt_path.exists():
            raise FileNotFoundError(f"SRT файл не найден: {srt_path}")
        
        if progress_callback:
            progress_callback("Чтение субтитров...", 10)
        
        # Читаем субтитры
        segments = parse_srt_file(srt_path)
        
        if not segments:
            raise ValueError("SRT файл пуст или не может быть прочитан")
        
        # Определяем язык если не указан
        if from_lang is None:
            if progress_callback:
                progress_callback("Определение языка...", 20)
            
            # Берём текст из первых нескольких сегментов для определения языка
            sample_text = ' '.join(seg.text for seg in segments[:5])
            from_lang = self.detect_language(sample_text)
            
            if not from_lang:
                from_lang = 'en'  # по умолчанию английский
        
        # Проверяем доступность перевода
        if not self.is_translation_available(from_lang, to_lang):
            if progress_callback:
                progress_callback("Установка языкового пакета...", 30)
            
            # Пытаемся установить пакет
            if not self.install_language_package(from_lang, to_lang):
                raise RuntimeError(
                    f"Перевод {from_lang} -> {to_lang} недоступен и не может быть установлен. "
                    f"Проверьте подключение к интернету для первой установки."
                )
        
        if progress_callback:
            progress_callback("Перевод субтитров...", 40)
        
        # Переводим сегменты
        translated_segments = []
        total = len(segments)
        
        for i, segment in enumerate(segments):
            try:
                translated_seg = self.translate_subtitle_segment(segment, from_lang, to_lang)
                translated_segments.append(translated_seg)
                
                if progress_callback:
                    progress = 40 + int((i + 1) / total * 50)
                    progress_callback(f"Перевод субтитров... {i+1}/{total}", progress)
            except Exception as e:
                # В случае ошибки оставляем оригинальный текст
                print(f"Ошибка перевода сегмента {segment.index}: {e}")
                translated_segments.append(segment)
        
        # Сохраняем результат
        if output_path is None:
            output_path = get_srt_path_for_media(srt_path, to_lang)
        
        if progress_callback:
            progress_callback("Сохранение переведённых субтитров...", 95)
        
        write_srt_file(output_path, translated_segments)
        
        if progress_callback:
            progress_callback("Готово", 100)
        
        return output_path


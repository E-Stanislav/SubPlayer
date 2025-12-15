"""Утилиты для работы с SRT файлами"""
from pathlib import Path
from typing import List, Tuple, Optional
import re


class SubtitleSegment:
    """Сегмент субтитров"""
    
    def __init__(self, index: int, start_time: float, end_time: float, text: str):
        self.index = index
        self.start_time = start_time  # в секундах
        self.end_time = end_time  # в секундах
        self.text = text
    
    def to_srt_time(self, seconds: float) -> str:
        """Преобразовать секунды в формат SRT (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def to_srt_string(self) -> str:
        """Преобразовать в строку SRT"""
        start_str = self.to_srt_time(self.start_time)
        end_str = self.to_srt_time(self.end_time)
        return f"{self.index}\n{start_str} --> {end_str}\n{self.text}\n"
    
    @staticmethod
    def from_srt_time(time_str: str) -> float:
        """Преобразовать формат SRT (HH:MM:SS,mmm) в секунды"""
        # Заменяем запятую на точку для парсинга
        time_str = time_str.replace(',', '.')
        parts = time_str.split(':')
        if len(parts) == 3:
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        return 0.0


def parse_srt_file(file_path: Path) -> List[SubtitleSegment]:
    """Парсить SRT файл"""
    segments = []
    
    if not file_path.exists():
        return segments
    
    content = file_path.read_text(encoding='utf-8')
    
    # Разделяем на блоки (двойной перевод строки)
    blocks = re.split(r'\n\s*\n', content.strip())
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        
        try:
            index = int(lines[0])
            time_line = lines[1]
            
            # Парсим время
            match = re.match(r'(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})', time_line)
            if match:
                start_time = SubtitleSegment.from_srt_time(match.group(1))
                end_time = SubtitleSegment.from_srt_time(match.group(2))
                
                # Текст - все остальные строки
                text = '\n'.join(lines[2:])
                
                segments.append(SubtitleSegment(index, start_time, end_time, text))
        except (ValueError, IndexError):
            continue
    
    return segments


def write_srt_file(file_path: Path, segments: List[SubtitleSegment]):
    """Записать SRT файл"""
    content = '\n\n'.join(seg.to_srt_string() for seg in segments)
    file_path.write_text(content, encoding='utf-8')


def get_srt_path_for_media(media_path: Path, language: Optional[str] = None) -> Path:
    """Получить путь к SRT файлу для медиа файла"""
    if language:
        return media_path.parent / f"{media_path.stem}.{language}.srt"
    return media_path.parent / f"{media_path.stem}.srt"


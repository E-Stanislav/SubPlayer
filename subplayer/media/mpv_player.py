"""Обёртка над mpv для воспроизведения медиа"""
import mpv
from PySide6.QtCore import QObject, Signal, QTimer
from pathlib import Path
import os


class MPVPlayer(QObject):
    """Обёртка над mpv с сигналами Qt"""
    
    # Сигналы
    position_changed = Signal(float)  # текущая позиция в секундах
    duration_changed = Signal(float)  # длительность в секундах
    state_changed = Signal(str)  # 'playing', 'paused', 'stopped'
    file_loaded = Signal(str)  # путь к загруженному файлу
    error_occurred = Signal(str)  # сообщение об ошибке
    
    def __init__(self, parent=None, widget_id=None):
        super().__init__(parent)
        
        self._widget_id = widget_id or int(os.environ.get('QT_WIDGET_ID', 0))
        self._player = None
        self._initialize_player()
        
        # Обработчики событий mpv
        @self._player.property_observer('time-pos')
        def time_observer(_name, value):
            if value is not None:
                self.position_changed.emit(float(value))
        
        @self._player.property_observer('duration')
        def duration_observer(_name, value):
            if value is not None:
                self.duration_changed.emit(float(value))
        
        @self._player.property_observer('pause')
        def pause_observer(_name, value):
            if value:
                self.state_changed.emit('paused')
            else:
                self.state_changed.emit('playing')
        
        # Таймер для обновления позиции (fallback)
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._update_position)
        self._update_timer.setInterval(100)  # 100ms
        
        self._current_file = None
        self._current_position = 0.0
        self._current_duration = 0.0
        self._is_playing = False
    
    def _initialize_player(self):
        """Инициализация mpv плеера"""
        try:
            # Создание mpv плеера
            # Используем wid для встраивания в Qt виджет
            player_kwargs = {
                'vo': 'gpu',
                'hwdec': 'auto',
                'input_default_bindings': True,
                'input_vo_keyboard': True,
                'osc': True,  # встроенный OSD
            }
            
            # Добавляем wid только если он задан
            if self._widget_id and self._widget_id > 0:
                player_kwargs['wid'] = str(self._widget_id)
            
            self._player = mpv.MPV(**player_kwargs)
            
            # Обработчики событий mpv
            @self._player.property_observer('time-pos')
            def time_observer(_name, value):
                if value is not None:
                    self.position_changed.emit(float(value))
            
            @self._player.property_observer('duration')
            def duration_observer(_name, value):
                if value is not None:
                    self.duration_changed.emit(float(value))
            
            @self._player.property_observer('pause')
            def pause_observer(_name, value):
                if value:
                    self.state_changed.emit('paused')
                else:
                    self.state_changed.emit('playing')
        except Exception as e:
            raise RuntimeError(f"Ошибка инициализации mpv: {str(e)}")
    
    def load_file(self, file_path: str):
        """Загрузить медиа файл"""
        try:
            path = Path(file_path)
            if not path.exists():
                self.error_occurred.emit(f"Файл не найден: {file_path}")
                return False
            
            self._current_file = str(path.absolute())
            self._player.play(self._current_file)
            self._update_timer.start()
            self.file_loaded.emit(self._current_file)
            return True
        except Exception as e:
            self.error_occurred.emit(f"Ошибка загрузки файла: {str(e)}")
            return False
    
    def play(self):
        """Начать воспроизведение"""
        try:
            self._player.pause = False
            self._is_playing = True
            self._update_timer.start()
        except Exception as e:
            self.error_occurred.emit(f"Ошибка воспроизведения: {str(e)}")
    
    def pause(self):
        """Приостановить воспроизведение"""
        try:
            self._player.pause = True
            self._is_playing = False
        except Exception as e:
            self.error_occurred.emit(f"Ошибка паузы: {str(e)}")
    
    def toggle_play_pause(self):
        """Переключить воспроизведение/паузу"""
        if self._is_playing:
            self.pause()
        else:
            self.play()
    
    def seek(self, position: float):
        """Перемотать на позицию (в секундах)"""
        try:
            self._player.seek(position, reference='absolute')
            self._current_position = position
        except Exception as e:
            self.error_occurred.emit(f"Ошибка перемотки: {str(e)}")
    
    def seek_relative(self, offset: float):
        """Перемотать относительно текущей позиции (в секундах)"""
        try:
            self._player.seek(offset, reference='relative')
        except Exception as e:
            self.error_occurred.emit(f"Ошибка перемотки: {str(e)}")
    
    def get_position(self) -> float:
        """Получить текущую позицию (в секундах)"""
        try:
            pos = self._player.time_pos
            if pos is not None:
                self._current_position = float(pos)
            return self._current_position
        except:
            return self._current_position
    
    def get_duration(self) -> float:
        """Получить длительность (в секундах)"""
        try:
            dur = self._player.duration
            if dur is not None:
                self._current_duration = float(dur)
            return self._current_duration
        except:
            return self._current_duration
    
    def is_playing(self) -> bool:
        """Проверить, играет ли плеер"""
        try:
            return not self._player.pause
        except:
            return self._is_playing
    
    def add_subtitle_file(self, subtitle_path: str):
        """Добавить файл субтитров"""
        try:
            path = Path(subtitle_path)
            if not path.exists():
                self.error_occurred.emit(f"Файл субтитров не найден: {subtitle_path}")
                return False
            
            # Добавляем субтитры через команду mpv
            self._player.sub_add(str(path.absolute()))
            return True
        except Exception as e:
            self.error_occurred.emit(f"Ошибка добавления субтитров: {str(e)}")
            return False
    
    def remove_subtitle_file(self, subtitle_path: str):
        """Удалить файл субтитров"""
        try:
            # Получаем список загруженных субтитров
            sub_count = self._player.sub_count
            for i in range(sub_count):
                sub_path = self._player.sub_file_path(i)
                if sub_path and Path(sub_path) == Path(subtitle_path):
                    self._player.sub_remove(i)
                    return True
            return False
        except Exception as e:
            self.error_occurred.emit(f"Ошибка удаления субтитров: {str(e)}")
            return False
    
    def set_subtitle_visibility(self, visible: bool):
        """Показать/скрыть субтитры"""
        try:
            self._player.sub_visibility = visible
        except Exception as e:
            self.error_occurred.emit(f"Ошибка изменения видимости субтитров: {str(e)}")
    
    def get_widget_id(self) -> int:
        """Получить ID виджета для встраивания mpv"""
        # Для Qt нужно получить native widget ID
        # Это будет установлено извне через set_widget_id
        return getattr(self, '_widget_id', 0)
    
    def set_widget_id(self, widget_id: int):
        """Установить ID виджета для встраивания mpv"""
        if self._widget_id != widget_id:
            self._widget_id = widget_id
            # Пересоздаём плеер с новым wid
            if self._player:
                try:
                    self._player.terminate()
                except:
                    pass
            self._initialize_player()
    
    def _update_position(self):
        """Обновить позицию (fallback)"""
        pos = self.get_position()
        self.position_changed.emit(pos)
    
    def stop(self):
        """Остановить воспроизведение"""
        try:
            self._player.stop()
            self._is_playing = False
            self._update_timer.stop()
            self._current_position = 0.0
        except Exception as e:
            self.error_occurred.emit(f"Ошибка остановки: {str(e)}")
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            self._update_timer.stop()
            if hasattr(self, '_player'):
                self._player.terminate()
        except:
            pass


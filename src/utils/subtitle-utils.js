// Утилиты для работы с субтитрами

// Парсинг SRT формата
function parseSRT(content) {
    const subtitles = [];
    const blocks = content.trim().split(/\n\s*\n/);
    
    for (const block of blocks) {
        const lines = block.trim().split('\n');
        if (lines.length < 3) continue;
        
        const index = parseInt(lines[0]);
        if (isNaN(index)) continue;
        
        const timecode = lines[1];
        const timeMatch = timecode.match(/(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})/);
        if (!timeMatch) continue;
        
        const startTime = parseTime(timeMatch.slice(1, 5));
        const endTime = parseTime(timeMatch.slice(5, 9));
        const text = lines.slice(2).join('\n').trim();
        
        subtitles.push({
            index,
            startTime,
            endTime,
            text
        });
    }
    
    return subtitles.sort((a, b) => a.startTime - b.startTime);
}

// Преобразование времени из формата SRT в секунды
function parseTime(timeParts) {
    const hours = parseInt(timeParts[0]);
    const minutes = parseInt(timeParts[1]);
    const seconds = parseInt(timeParts[2]);
    const milliseconds = parseInt(timeParts[3]);
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000;
}

// Преобразование секунд в формат SRT
function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 1000);
    
    return `${pad(hours, 2)}:${pad(minutes, 2)}:${pad(secs, 2)},${pad(ms, 3)}`;
}

// Дополнение нулями
function pad(num, size) {
    let s = String(num);
    while (s.length < size) s = '0' + s;
    return s;
}

// Генерация SRT файла
function generateSRT(subtitles) {
    return subtitles
        .sort((a, b) => a.startTime - b.startTime)
        .map((sub, index) => {
            return `${index + 1}\n${formatTime(sub.startTime)} --> ${formatTime(sub.endTime)}\n${sub.text}\n`;
        })
        .join('\n');
}

// Форматирование времени для отображения (MM:SS или HH:MM:SS)
function formatDisplayTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
        return `${hours}:${pad(minutes, 2)}:${pad(secs, 2)}`;
    }
    return `${minutes}:${pad(secs, 2)}`;
}

// Преобразование строки времени (MM:SS.mmm или MM:SS) в секунды
function parseTimeString(timeString) {
    if (!timeString) return 0;
    
    const parts = timeString.trim().split(':');
    if (parts.length === 2) {
        const minutes = parseInt(parts[0]) || 0;
        const seconds = parseFloat(parts[1]) || 0;
        return minutes * 60 + seconds;
    } else if (parts.length === 3) {
        const hours = parseInt(parts[0]) || 0;
        const minutes = parseInt(parts[1]) || 0;
        const seconds = parseFloat(parts[2]) || 0;
        return hours * 3600 + minutes * 60 + seconds;
    }
    return 0;
}

// Преобразование секунд в строку времени (MM:SS.mmm)
function formatTimeString(seconds) {
    if (isNaN(seconds) || seconds < 0) return '0:00.000';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = (seconds % 60);
    const secsInt = Math.floor(secs);
    const milliseconds = Math.floor((secs - secsInt) * 1000);
    
    if (hours > 0) {
        return `${hours}:${pad(minutes, 2)}:${pad(secsInt, 2)}.${pad(milliseconds, 3)}`;
    }
    return `${minutes}:${pad(secsInt, 2)}.${pad(milliseconds, 3)}`;
}


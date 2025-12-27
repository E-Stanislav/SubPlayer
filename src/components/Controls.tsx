import { useCallback, useRef, useState } from 'react'

interface ControlsProps {
  isVisible: boolean
  isPlaying: boolean
  currentTime: number
  duration: number
  volume: number
  isMuted: boolean
  isFullscreen: boolean
  onTogglePlay: () => void
  onSeek: (time: number) => void
  onVolumeChange: (volume: number) => void
  onToggleMute: () => void
  onToggleFullscreen: () => void
  onReset: () => void
  ttsEnabled?: boolean
  onToggleTts?: () => void
  hasTtsAudio?: boolean
  showSubtitles?: boolean
  showTranslation?: boolean
  onToggleSubtitles?: () => void
  onToggleTranslation?: () => void
}

export default function Controls({
  isVisible,
  isPlaying,
  currentTime,
  duration,
  volume,
  isMuted,
  isFullscreen,
  onTogglePlay,
  onSeek,
  onVolumeChange,
  onToggleMute,
  onToggleFullscreen,
  onReset,
  ttsEnabled = false,
  onToggleTts,
  hasTtsAudio = false,
  showSubtitles = true,
  showTranslation = true,
  onToggleSubtitles,
  onToggleTranslation
}: ControlsProps) {
  const progressRef = useRef<HTMLDivElement>(null)
  const [isHoveringProgress, setIsHoveringProgress] = useState(false)
  const [hoverTime, setHoverTime] = useState(0)
  const [showVolumeSlider, setShowVolumeSlider] = useState(false)

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleProgressClick = useCallback((e: React.MouseEvent) => {
    if (progressRef.current) {
      const rect = progressRef.current.getBoundingClientRect()
      const pos = (e.clientX - rect.left) / rect.width
      onSeek(pos * duration)
    }
  }, [duration, onSeek])

  const handleProgressHover = useCallback((e: React.MouseEvent) => {
    if (progressRef.current) {
      const rect = progressRef.current.getBoundingClientRect()
      const pos = (e.clientX - rect.left) / rect.width
      setHoverTime(pos * duration)
    }
  }, [duration])

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0

  return (
    <div 
      className={`
        absolute bottom-0 left-0 right-0 
        bg-gradient-to-t from-black/90 via-black/50 to-transparent
        transition-opacity duration-300
        ${isVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'}
      `}
    >
      {/* Progress bar */}
      <div 
        ref={progressRef}
        className="relative h-1 mx-4 mb-2 cursor-pointer group"
        onClick={handleProgressClick}
        onMouseEnter={() => setIsHoveringProgress(true)}
        onMouseLeave={() => setIsHoveringProgress(false)}
        onMouseMove={handleProgressHover}
      >
        {/* Background track */}
        <div className="absolute inset-0 bg-white/20 rounded-full" />
        
        {/* Buffered indicator */}
        <div 
          className="absolute inset-y-0 left-0 bg-white/30 rounded-full"
          style={{ width: `${Math.min(progress + 10, 100)}%` }}
        />
        
        {/* Progress track */}
        <div 
          className="absolute inset-y-0 left-0 bg-player-accent rounded-full transition-all"
          style={{ width: `${progress}%` }}
        />
        
        {/* Hover indicator */}
        {isHoveringProgress && (
          <div 
            className="absolute -top-8 transform -translate-x-1/2 bg-black/80 px-2 py-1 rounded text-xs text-white"
            style={{ left: `${(hoverTime / duration) * 100}%` }}
          >
            {formatTime(hoverTime)}
          </div>
        )}
        
        {/* Scrubber handle */}
        <div 
          className={`
            absolute top-1/2 -translate-y-1/2 w-3 h-3 bg-player-accent rounded-full
            shadow-lg shadow-player-accent/50 transition-transform
            ${isHoveringProgress ? 'scale-125' : 'scale-0 group-hover:scale-100'}
          `}
          style={{ left: `${progress}%`, transform: `translateX(-50%) translateY(-50%)` }}
        />
      </div>

      {/* Controls row */}
      <div className="flex items-center justify-between px-4 pb-4">
        {/* Left controls */}
        <div className="flex items-center gap-2">
          {/* Back button */}
          <button
            onClick={onReset}
            className="p-2 rounded-full hover:bg-white/10 transition-colors no-drag"
            title="Новое видео"
          >
            <svg className="w-5 h-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          {/* Play/Pause */}
          <button
            onClick={onTogglePlay}
            className="p-2 rounded-full hover:bg-white/10 transition-colors no-drag"
          >
            {isPlaying ? (
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
              </svg>
            ) : (
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>

          {/* Skip backward */}
          <button
            onClick={() => onSeek(Math.max(0, currentTime - 10))}
            className="p-2 rounded-full hover:bg-white/10 transition-colors no-drag"
            title="-10 сек"
          >
            <svg className="w-5 h-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" />
            </svg>
          </button>

          {/* Skip forward */}
          <button
            onClick={() => onSeek(Math.min(duration, currentTime + 10))}
            className="p-2 rounded-full hover:bg-white/10 transition-colors no-drag"
            title="+10 сек"
          >
            <svg className="w-5 h-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z" />
            </svg>
          </button>

          {/* Volume control */}
          <div 
            className="relative flex items-center"
            onMouseEnter={() => setShowVolumeSlider(true)}
            onMouseLeave={() => setShowVolumeSlider(false)}
          >
            <button
              onClick={onToggleMute}
              className="p-2 rounded-full hover:bg-white/10 transition-colors no-drag"
            >
              {isMuted || volume === 0 ? (
                <svg className="w-5 h-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                </svg>
              ) : volume < 0.5 ? (
                <svg className="w-5 h-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                </svg>
              )}
            </button>
            
            {/* Volume slider */}
            <div className={`
              absolute left-full ml-1 flex items-center h-8 px-2
              bg-black/80 rounded-full transition-all
              ${showVolumeSlider ? 'opacity-100 w-24' : 'opacity-0 w-0 overflow-hidden'}
            `}>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={isMuted ? 0 : volume}
                onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
                className="w-full h-1 bg-white/30 rounded-full appearance-none cursor-pointer no-drag
                  [&::-webkit-slider-thumb]:appearance-none
                  [&::-webkit-slider-thumb]:w-3
                  [&::-webkit-slider-thumb]:h-3
                  [&::-webkit-slider-thumb]:rounded-full
                  [&::-webkit-slider-thumb]:bg-player-accent
                "
              />
            </div>
          </div>

          {/* Time display */}
          <span className="text-sm text-white/70 ml-2 tabular-nums">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
        </div>

        {/* Right controls */}
        <div className="flex items-center gap-2">
          {/* Toggle Russian translation */}
          {onToggleTranslation && (
            <button
              onClick={onToggleTranslation}
              className={`
                p-2 rounded-full transition-colors no-drag
                ${showTranslation && showSubtitles
                  ? 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30' 
                  : 'hover:bg-white/10 text-white/40'
                }
              `}
              title={showTranslation ? 'Скрыть русские субтитры (R)' : 'Показать русские субтитры (R)'}
              disabled={!showSubtitles}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
              </svg>
            </button>
          )}

          {/* Toggle all subtitles */}
          {onToggleSubtitles && (
            <button
              onClick={onToggleSubtitles}
              className={`
                p-2 rounded-full transition-colors no-drag
                ${showSubtitles
                  ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' 
                  : 'hover:bg-white/10 text-white/40'
                }
              `}
              title={showSubtitles ? 'Скрыть все субтитры (S)' : 'Показать все субтитры (S)'}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
            </button>
          )}

          {/* TTS Toggle */}
          {hasTtsAudio && onToggleTts && (
            <button
              onClick={onToggleTts}
              className={`
                p-2 rounded-full transition-colors no-drag
                ${ttsEnabled 
                  ? 'bg-orange-500/20 text-orange-400 hover:bg-orange-500/30' 
                  : 'hover:bg-white/10 text-white/60'
                }
              `}
              title={ttsEnabled ? 'Выключить озвучку (T)' : 'Включить озвучку (T)'}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </button>
          )}

          {/* Fullscreen */}
          <button
            onClick={onToggleFullscreen}
            className="p-2 rounded-full hover:bg-white/10 transition-colors no-drag"
            title="Полный экран (F)"
          >
            {isFullscreen ? (
              <svg className="w-5 h-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

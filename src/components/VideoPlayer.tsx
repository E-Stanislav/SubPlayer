import { useRef, useState, useEffect, useCallback } from 'react'
import Controls from './Controls'
import Subtitles from './Subtitles'
import type { Subtitle } from '../App'

interface VideoPlayerProps {
  src: string
  subtitles: Subtitle[]
  onReset: () => void
  isProcessing?: boolean
  subtitleCount?: number
  ttsEnabled?: boolean
  onToggleTts?: () => void
  hasTtsAudio?: boolean
}

export default function VideoPlayer({ 
  src, 
  subtitles, 
  onReset, 
  isProcessing = false,
  subtitleCount = 0,
  ttsEnabled = false,
  onToggleTts,
  hasTtsAudio = false
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const ttsAudioRef = useRef<HTMLAudioElement>(null)
  const [ttsAudioSrc, setTtsAudioSrc] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showControls, setShowControls] = useState(true)
  const [currentSubtitle, setCurrentSubtitle] = useState<Subtitle | null>(null)
  const [playingTtsId, setPlayingTtsId] = useState<number | null>(null)
  const hideControlsTimeout = useRef<NodeJS.Timeout | null>(null)

  // Find current subtitle based on video time
  useEffect(() => {
    const subtitle = subtitles.find(
      sub => currentTime >= sub.start && currentTime <= sub.end
    )
    setCurrentSubtitle(subtitle || null)
  }, [currentTime, subtitles])

  // Play TTS audio when subtitle changes (if TTS enabled)
  useEffect(() => {
    if (!ttsEnabled || !currentSubtitle?.audioFile) {
      return
    }

    // Don't replay if same subtitle
    if (playingTtsId === currentSubtitle.id) {
      return
    }

    const subtitleId = currentSubtitle.id
    const audioFilePath = currentSubtitle.audioFile

    // Load and play TTS audio through IPC
    const loadTts = async () => {
      console.log('Loading TTS file:', audioFilePath)
      
      const audioDataUrl = await window.electron?.readAudioFile(audioFilePath)
      
      if (!audioDataUrl) {
        console.error('Failed to load TTS audio file')
        return
      }
      
      console.log('TTS audio loaded, data length:', audioDataUrl.length)
      setTtsAudioSrc(audioDataUrl)
      setPlayingTtsId(subtitleId)
    }

    loadTts()
  }, [currentSubtitle, ttsEnabled, playingTtsId])

  // Handle TTS audio element events
  useEffect(() => {
    const audio = ttsAudioRef.current
    if (!audio || !ttsAudioSrc) return

    const handleCanPlay = () => {
      console.log('TTS audio ready, duration:', audio.duration, 'seconds')
      
      // Lower video volume during TTS
      if (videoRef.current) {
        videoRef.current.volume = volume * 0.15
      }

      audio.play()
        .then(() => console.log('TTS playback started'))
        .catch(err => {
          console.error('TTS playback failed:', err)
          if (videoRef.current) {
            videoRef.current.volume = volume
          }
        })
    }

    const handleEnded = () => {
      console.log('TTS playback ended')
      if (videoRef.current) {
        videoRef.current.volume = volume
      }
      setPlayingTtsId(null)
      setTtsAudioSrc(null)
    }

    const handleError = (e: Event) => {
      console.error('TTS audio error:', e, audio.error)
      if (videoRef.current) {
        videoRef.current.volume = volume
      }
      setPlayingTtsId(null)
      setTtsAudioSrc(null)
    }

    audio.addEventListener('canplaythrough', handleCanPlay)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('error', handleError)

    return () => {
      audio.removeEventListener('canplaythrough', handleCanPlay)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('error', handleError)
    }
  }, [ttsAudioSrc, volume])

  // Sync TTS audio volume
  useEffect(() => {
    if (ttsAudioRef.current && ttsAudioSrc) {
      ttsAudioRef.current.volume = volume
    }
  }, [volume, ttsAudioSrc])

  // Stop TTS when disabled
  useEffect(() => {
    if (!ttsEnabled && ttsAudioRef.current && ttsAudioSrc) {
      ttsAudioRef.current.pause()
      setTtsAudioSrc(null)
      setPlayingTtsId(null)
      // Restore video volume
      if (videoRef.current) {
        videoRef.current.volume = volume
      }
    }
  }, [ttsEnabled, volume, ttsAudioSrc])

  // Handle mouse movement for controls visibility
  const handleMouseMove = useCallback(() => {
    setShowControls(true)
    if (hideControlsTimeout.current) {
      clearTimeout(hideControlsTimeout.current)
    }
    if (isPlaying) {
      hideControlsTimeout.current = setTimeout(() => {
        setShowControls(false)
      }, 3000)
    }
  }, [isPlaying])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (hideControlsTimeout.current) {
        clearTimeout(hideControlsTimeout.current)
      }
    }
  }, [])

  // Video event handlers
  const handleTimeUpdate = useCallback(() => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
    }
  }, [])

  const handleLoadedMetadata = useCallback(() => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration)
    }
  }, [])

  const handlePlay = useCallback(() => setIsPlaying(true), [])
  const handlePause = useCallback(() => {
    setIsPlaying(false)
    // Pause TTS too
    ttsAudioRef.current?.pause()
  }, [])

  // Control functions
  const togglePlay = useCallback(() => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
    }
  }, [isPlaying])

  const handleSeek = useCallback((time: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = time
      setCurrentTime(time)
      // Stop current TTS on seek
      if (ttsAudioRef.current && ttsAudioSrc) {
        ttsAudioRef.current.pause()
        setTtsAudioSrc(null)
        setPlayingTtsId(null)
      }
    }
  }, [ttsAudioSrc])

  const handleVolumeChange = useCallback((newVolume: number) => {
    if (videoRef.current) {
      videoRef.current.volume = ttsEnabled && playingTtsId ? newVolume * 0.15 : newVolume
      setVolume(newVolume)
      setIsMuted(newVolume === 0)
    }
  }, [ttsEnabled, playingTtsId])

  const toggleMute = useCallback(() => {
    if (videoRef.current) {
      const newMuted = !isMuted
      videoRef.current.muted = newMuted
      setIsMuted(newMuted)
      if (ttsAudioRef.current) {
        ttsAudioRef.current.muted = newMuted
      }
    }
  }, [isMuted])

  const toggleFullscreen = useCallback(async () => {
    if (!containerRef.current) return

    if (!document.fullscreenElement) {
      await containerRef.current.requestFullscreen()
      setIsFullscreen(true)
    } else {
      await document.exitFullscreen()
      setIsFullscreen(false)
    }
  }, [])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.code) {
        case 'Space':
          e.preventDefault()
          togglePlay()
          break
        case 'ArrowLeft':
          handleSeek(Math.max(0, currentTime - 5))
          break
        case 'ArrowRight':
          handleSeek(Math.min(duration, currentTime + 5))
          break
        case 'ArrowUp':
          handleVolumeChange(Math.min(1, volume + 0.1))
          break
        case 'ArrowDown':
          handleVolumeChange(Math.max(0, volume - 0.1))
          break
        case 'KeyM':
          toggleMute()
          break
        case 'KeyF':
          toggleFullscreen()
          break
        case 'KeyT':
          // Toggle TTS with T key
          if (onToggleTts && hasTtsAudio) {
            onToggleTts()
          }
          break
        case 'Escape':
          if (isFullscreen) {
            document.exitFullscreen()
          }
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [togglePlay, handleSeek, handleVolumeChange, toggleMute, toggleFullscreen, currentTime, duration, volume, isFullscreen, onToggleTts, hasTtsAudio])

  // Handle fullscreen change
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }

    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }, [])

  return (
    <div 
      ref={containerRef}
      className="relative w-full h-full bg-black flex items-center justify-center"
      onMouseMove={handleMouseMove}
      onMouseLeave={() => isPlaying && setShowControls(false)}
    >
      {/* Video element */}
      <video
        ref={videoRef}
        src={src}
        className="max-w-full max-h-full"
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onPlay={handlePlay}
        onPause={handlePause}
        onClick={togglePlay}
      />

      {/* Hidden TTS audio element */}
      <audio 
        ref={ttsAudioRef}
        src={ttsAudioSrc || undefined}
        preload="auto"
      />

      {/* Status indicators */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        {/* Processing indicator */}
        {isProcessing && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/70 backdrop-blur-sm">
            <div className="w-2 h-2 rounded-full bg-player-accent animate-pulse" />
            <span className="text-xs text-white/80">
              Обработка... {subtitleCount} субтитров
            </span>
          </div>
        )}
        
        {/* TTS indicator */}
        {ttsEnabled && hasTtsAudio && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-500/20 backdrop-blur-sm border border-orange-500/30">
            <svg className="w-4 h-4 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
            <span className="text-xs text-orange-400">Озвучка вкл</span>
          </div>
        )}
      </div>

      {/* Subtitles overlay */}
      <Subtitles subtitle={currentSubtitle} />

      {/* Controls overlay */}
      <Controls
        isVisible={showControls}
        isPlaying={isPlaying}
        currentTime={currentTime}
        duration={duration}
        volume={volume}
        isMuted={isMuted}
        isFullscreen={isFullscreen}
        onTogglePlay={togglePlay}
        onSeek={handleSeek}
        onVolumeChange={handleVolumeChange}
        onToggleMute={toggleMute}
        onToggleFullscreen={toggleFullscreen}
        onReset={onReset}
        ttsEnabled={ttsEnabled}
        onToggleTts={onToggleTts}
        hasTtsAudio={hasTtsAudio}
      />

      {/* Click to play overlay (when paused) */}
      {!isPlaying && (
        <div 
          className="absolute inset-0 flex items-center justify-center cursor-pointer"
          onClick={togglePlay}
        >
          <div className="w-20 h-20 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center transition-transform hover:scale-110">
            <svg className="w-10 h-10 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      )}
    </div>
  )
}

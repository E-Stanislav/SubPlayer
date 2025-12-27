import { useState, useCallback } from 'react'
import VideoPlayer from './components/VideoPlayer'
import FileUpload from './components/FileUpload'
import ProcessingOverlay from './components/ProcessingOverlay'
import { useSubtitles } from './hooks/useSubtitles'

export interface Subtitle {
  id: number
  start: number
  end: number
  text: string
  translatedText?: string
  audioFile?: string | null
}

export interface ProcessingStatus {
  stage: 'idle' | 'extracting' | 'transcribing' | 'translating' | 'done' | 'error'
  progress: number
  message: string
}

function App() {
  const [videoSrc, setVideoSrc] = useState<string | null>(null)
  const [enableTts, setEnableTts] = useState(false)
  const [ttsEnabled, setTtsEnabled] = useState(false) // Whether TTS is active during playback
  const { 
    subtitles, 
    processingStatus, 
    isStreaming,
    processVideo, 
    clearSubtitles 
  } = useSubtitles()

  const handleFileSelect = useCallback(async (filePath: string, withTts: boolean) => {
    // Clear previous state
    clearSubtitles()
    setEnableTts(withTts)
    setTtsEnabled(withTts)
    
    // Create file URL for video playback
    const fileUrl = `file://${filePath}`
    setVideoSrc(fileUrl)
    
    // Start processing with TTS option
    await processVideo(filePath, withTts)
  }, [processVideo, clearSubtitles])

  const handleReset = useCallback(() => {
    setVideoSrc(null)
    setEnableTts(false)
    setTtsEnabled(false)
    clearSubtitles()
  }, [clearSubtitles])

  const handleToggleTts = useCallback(() => {
    setTtsEnabled(prev => !prev)
  }, [])

  // Show processing indicator but allow playback during streaming
  const showProcessingOverlay = processingStatus.stage !== 'idle' && 
                                 processingStatus.stage !== 'done' && 
                                 processingStatus.stage !== 'error' &&
                                 subtitles.length === 0

  // Check if TTS audio is available
  const hasTtsAudio = subtitles.some(s => s.audioFile)

  return (
    <div className="w-full h-full flex flex-col bg-player-bg">
      {/* Title bar drag area */}
      <div className="drag-area h-8 flex items-center justify-center bg-player-surface/50 border-b border-white/5">
        <span className="text-xs text-white/40 font-medium tracking-wider">SUBPLAYER</span>
      </div>

      {/* Main content */}
      <div className="flex-1 relative overflow-hidden">
        {!videoSrc ? (
          <FileUpload onFileSelect={handleFileSelect} />
        ) : (
          <>
            <VideoPlayer 
              src={videoSrc} 
              subtitles={subtitles}
              onReset={handleReset}
              isProcessing={isStreaming}
              subtitleCount={subtitles.length}
              ttsEnabled={ttsEnabled && hasTtsAudio}
              onToggleTts={handleToggleTts}
              hasTtsAudio={hasTtsAudio}
            />
            {showProcessingOverlay && (
              <ProcessingOverlay status={processingStatus} />
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default App

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
}

export interface ProcessingStatus {
  stage: 'idle' | 'extracting' | 'transcribing' | 'translating' | 'done' | 'error'
  progress: number
  message: string
}

function App() {
  const [videoSrc, setVideoSrc] = useState<string | null>(null)
  const [videoPath, setVideoPath] = useState<string | null>(null)
  const { 
    subtitles, 
    processingStatus, 
    processVideo, 
    clearSubtitles 
  } = useSubtitles()

  const handleFileSelect = useCallback(async (filePath: string) => {
    // Clear previous state
    clearSubtitles()
    
    // Create file URL for video playback
    const fileUrl = `file://${filePath}`
    setVideoSrc(fileUrl)
    setVideoPath(filePath)
    
    // Start processing
    await processVideo(filePath)
  }, [processVideo, clearSubtitles])

  const handleReset = useCallback(() => {
    setVideoSrc(null)
    setVideoPath(null)
    clearSubtitles()
  }, [clearSubtitles])

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
            />
            {processingStatus.stage !== 'idle' && processingStatus.stage !== 'done' && (
              <ProcessingOverlay status={processingStatus} />
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default App


/// <reference types="vite/client" />

interface Window {
  electron: {
    openFile: () => Promise<string | null>
    processVideo: (videoPath: string, onProgress: (status: ProcessingUpdate) => void) => Promise<SubtitleResult[]>
    onProcessingUpdate: (callback: (update: ProcessingUpdate) => void) => void
    removeProcessingListener: () => void
  }
}

interface ProcessingUpdate {
  stage: 'extracting' | 'transcribing' | 'translating' | 'done' | 'error'
  progress: number
  message: string
}

interface SubtitleResult {
  id: number
  start: number
  end: number
  text: string
  translatedText: string
}


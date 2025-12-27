/// <reference types="vite/client" />

interface Window {
  electron: {
    openFile: () => Promise<string | null>
    processVideo: (videoPath: string, enableTts?: boolean) => Promise<SubtitleResult[]>
    onProcessingUpdate: (callback: (update: ProcessingUpdate) => void) => void
    onSubtitleReady: (callback: (subtitle: SubtitleResult) => void) => void
    removeProcessingListener: () => void
    removeSubtitleListener: () => void
    readAudioFile: (filePath: string) => Promise<string | null>
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
  audioFile?: string | null
}

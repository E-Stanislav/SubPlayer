import { useState, useCallback, useRef } from 'react'
import type { Subtitle, ProcessingStatus } from '../App'

const initialStatus: ProcessingStatus = {
  stage: 'idle',
  progress: 0,
  message: ''
}

export function useSubtitles() {
  const [subtitles, setSubtitles] = useState<Subtitle[]>([])
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatus>(initialStatus)
  const [isStreaming, setIsStreaming] = useState(false)
  const subtitlesRef = useRef<Subtitle[]>([])

  const processVideo = useCallback(async (videoPath: string) => {
    if (!window.electron) {
      console.error('Electron API not available')
      setProcessingStatus({
        stage: 'error',
        progress: 0,
        message: 'Electron API недоступен. Запустите приложение через Electron.'
      })
      return
    }

    try {
      // Reset state
      subtitlesRef.current = []
      setSubtitles([])
      setIsStreaming(true)

      // Set up progress listener
      window.electron.onProcessingUpdate((update) => {
        setProcessingStatus({
          stage: update.stage,
          progress: update.progress,
          message: update.message
        })
      })

      // Set up streaming subtitle listener - add subtitles as they arrive
      window.electron.onSubtitleReady((subtitle) => {
        subtitlesRef.current = [...subtitlesRef.current, subtitle]
        setSubtitles([...subtitlesRef.current])
      })

      // Start processing
      setProcessingStatus({
        stage: 'extracting',
        progress: 0,
        message: 'Подготовка к обработке...'
      })

      // This will return when all subtitles are ready, but we're streaming them
      await window.electron.processVideo(videoPath, (update) => {
        setProcessingStatus({
          stage: update.stage,
          progress: update.progress,
          message: update.message
        })
      })

      setProcessingStatus({
        stage: 'done',
        progress: 100,
        message: 'Готово!'
      })

    } catch (error) {
      console.error('Processing error:', error)
      setProcessingStatus({
        stage: 'error',
        progress: 0,
        message: error instanceof Error ? error.message : 'Неизвестная ошибка'
      })
    } finally {
      setIsStreaming(false)
      // Clean up listeners
      if (window.electron) {
        window.electron.removeProcessingListener()
        window.electron.removeSubtitleListener()
      }
    }
  }, [])

  const clearSubtitles = useCallback(() => {
    subtitlesRef.current = []
    setSubtitles([])
    setProcessingStatus(initialStatus)
    setIsStreaming(false)
  }, [])

  return {
    subtitles,
    processingStatus,
    isStreaming,
    processVideo,
    clearSubtitles
  }
}

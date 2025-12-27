import { useState, useCallback } from 'react'
import type { Subtitle, ProcessingStatus } from '../App'

const initialStatus: ProcessingStatus = {
  stage: 'idle',
  progress: 0,
  message: ''
}

export function useSubtitles() {
  const [subtitles, setSubtitles] = useState<Subtitle[]>([])
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatus>(initialStatus)

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
      // Set up progress listener
      window.electron.onProcessingUpdate((update) => {
        setProcessingStatus({
          stage: update.stage,
          progress: update.progress,
          message: update.message
        })

        if (update.stage === 'done') {
          setProcessingStatus(prev => ({ ...prev, stage: 'done' }))
        }
      })

      // Start processing
      setProcessingStatus({
        stage: 'extracting',
        progress: 0,
        message: 'Подготовка к обработке...'
      })

      const result = await window.electron.processVideo(videoPath, (update) => {
        setProcessingStatus({
          stage: update.stage,
          progress: update.progress,
          message: update.message
        })
      })

      // Set subtitles
      setSubtitles(result)
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
      // Clean up listener
      if (window.electron) {
        window.electron.removeProcessingListener()
      }
    }
  }, [])

  const clearSubtitles = useCallback(() => {
    setSubtitles([])
    setProcessingStatus(initialStatus)
  }, [])

  return {
    subtitles,
    processingStatus,
    processVideo,
    clearSubtitles
  }
}


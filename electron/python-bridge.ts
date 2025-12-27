import { spawn, ChildProcess } from 'child_process'
import { join } from 'path'
import { existsSync } from 'fs'

// Get process.env before any variable shadowing
const nodeEnv = process.env

interface Subtitle {
  id: number
  start: number
  end: number
  text: string
  translatedText: string
}

interface ProgressCallback {
  (update: { stage: string; progress: number; message: string }): void
}

interface SubtitleCallback {
  (subtitle: Subtitle): void
}

export class PythonBridge {
  private pythonPath: string
  private pythonExecutable: string

  constructor(pythonPath: string) {
    this.pythonPath = pythonPath
    // Try to find Python executable, preferring venv
    this.pythonExecutable = this.findPythonExecutable()
  }

  private findPythonExecutable(): string {
    // First, check for venv in python directory (dev mode)
    const venvPython = join(this.pythonPath, 'venv', 'bin', 'python')
    if (existsSync(venvPython)) {
      return venvPython
    }

    // Check for venv in workspace root (when running from source)
    const workspaceVenv = join(this.pythonPath, '..', 'python', 'venv', 'bin', 'python')
    if (existsSync(workspaceVenv)) {
      return workspaceVenv
    }

    // Check for common Python paths (production mode - uses system Python)
    const candidates = [
      '/opt/homebrew/bin/python3',  // Homebrew on Apple Silicon
      '/usr/local/bin/python3',      // Homebrew on Intel
      '/usr/bin/python3',            // System Python
      'python3',
      'python'
    ]

    for (const candidate of candidates) {
      if (existsSync(candidate) || candidate === 'python3' || candidate === 'python') {
        return candidate
      }
    }

    return 'python3' // Default fallback
  }

  async processVideo(
    videoPath: string, 
    onProgress: ProgressCallback,
    onSubtitle?: SubtitleCallback
  ): Promise<Subtitle[]> {
    const scriptPath = join(this.pythonPath, 'process.py')
    
    // Check if script exists
    if (!existsSync(scriptPath)) {
      throw new Error(`Python script not found: ${scriptPath}`)
    }

    return new Promise((resolve, reject) => {
      const pythonProcess: ChildProcess = spawn(this.pythonExecutable, [
        scriptPath,
        videoPath
      ], {
        cwd: this.pythonPath,
        env: { ...nodeEnv, PYTHONUNBUFFERED: '1' }
      })

      let outputBuffer = ''
      let errorBuffer = ''
      const subtitles: Subtitle[] = []

      pythonProcess.stdout?.on('data', (data: Buffer) => {
        const text = data.toString()
        outputBuffer += text

        // Parse messages from stdout
        const lines = text.split('\n')
        for (const line of lines) {
          // Progress updates
          if (line.startsWith('PROGRESS:')) {
            try {
              const progressData = JSON.parse(line.substring(9))
              onProgress(progressData)
            } catch (e) {
              console.error('Failed to parse progress:', e)
            }
          }
          // Streaming subtitles - send immediately to UI
          else if (line.startsWith('SUBTITLE:')) {
            try {
              const subtitle = JSON.parse(line.substring(9)) as Subtitle
              subtitles.push(subtitle)
              if (onSubtitle) {
                onSubtitle(subtitle)
              }
            } catch (e) {
              console.error('Failed to parse subtitle:', e)
            }
          }
        }
      })

      pythonProcess.stderr?.on('data', (data: Buffer) => {
        errorBuffer += data.toString()
        console.error('Python stderr:', data.toString())
      })

      pythonProcess.on('close', (code: number | null) => {
        if (code === 0) {
          // Return collected subtitles (also available from RESULT for backwards compat)
          if (subtitles.length > 0) {
            resolve(subtitles)
          } else {
            // Fallback: parse RESULT if no streaming subtitles
            const jsonMatch = outputBuffer.match(/RESULT:(\{.*\})/s)
            if (jsonMatch) {
              try {
                const result = JSON.parse(jsonMatch[1])
                resolve(result.subtitles || [])
              } catch (e) {
                reject(new Error(`Failed to parse result: ${e}`))
              }
            } else {
              resolve([])
            }
          }
        } else {
          reject(new Error(`Process exited with code ${code}: ${errorBuffer}`))
        }
      })

      pythonProcess.on('error', (err: Error) => {
        reject(new Error(`Failed to start Python process: ${err.message}`))
      })
    })
  }
}

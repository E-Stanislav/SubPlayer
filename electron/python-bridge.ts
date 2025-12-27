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

export class PythonBridge {
  private pythonPath: string
  private pythonExecutable: string

  constructor(pythonPath: string) {
    this.pythonPath = pythonPath
    // Try to find Python executable, preferring venv
    this.pythonExecutable = this.findPythonExecutable()
  }

  private findPythonExecutable(): string {
    // First, check for venv in python directory
    const venvPython = join(this.pythonPath, 'venv', 'bin', 'python')
    if (existsSync(venvPython)) {
      return venvPython
    }

    // Check for common Python paths
    const candidates = [
      'python3',
      'python',
      '/usr/bin/python3',
      '/usr/local/bin/python3',
      '/opt/homebrew/bin/python3'
    ]

    for (const candidate of candidates) {
      try {
        const result = spawn(candidate, ['--version'], { stdio: 'pipe' })
        if (result.pid) {
          result.kill()
          return candidate
        }
      } catch {
        continue
      }
    }

    return 'python3' // Default fallback
  }

  async processVideo(videoPath: string, onProgress: ProgressCallback): Promise<Subtitle[]> {
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

      pythonProcess.stdout?.on('data', (data: Buffer) => {
        const text = data.toString()
        outputBuffer += text

        // Parse progress updates from stdout
        const lines = text.split('\n')
        for (const line of lines) {
          if (line.startsWith('PROGRESS:')) {
            try {
              const progressData = JSON.parse(line.substring(9))
              onProgress(progressData)
            } catch (e) {
              console.error('Failed to parse progress:', e)
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
          // Find the JSON result in output
          const jsonMatch = outputBuffer.match(/RESULT:(\{.*\})/s)
          if (jsonMatch) {
            try {
              const result = JSON.parse(jsonMatch[1])
              resolve(result.subtitles || [])
            } catch (e) {
              reject(new Error(`Failed to parse result: ${e}`))
            }
          } else {
            reject(new Error('No result found in output'))
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


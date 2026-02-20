import React, { useEffect, useRef, useState } from 'react'
import { useApp } from './context/AppContext'
import InputSection from './components/InputSection'
import RunSummary from './components/RunSummary'
import ScoreBreakdown from './components/ScoreBreakdown'
import FixesTable from './components/FixesTable'
import Timeline from './components/Timeline'
import DownloadResults from './components/DownloadResults'
import './App.css'

const POLL_INTERVAL = 2000

const STATUS_MESSAGES = [
  "🔍 Analyzing repository structure...",
  "🔎 Discovering test files and source code...",
  "🐛 Scanning for errors and bugs...",
  "📊 Classifying error types...",
  "🤔 Thinking about the best fix strategy...",
  "⚙️ Resolving errors...",
  "🔧 Applying fixes...",
  "✅ Validating fixes...",
  "📝 Committing changes...",
  "🚀 Pushing to repository...",
]

export default function App() {
  const { runState, pollResult } = useApp()
  const pollRef = useRef(null)
  const [statusMessage, setStatusMessage] = useState("")
  const statusIndexRef = useRef(0)
  const startTimeRef = useRef(null)
  const [elapsedTime, setElapsedTime] = useState(0)

  useEffect(() => {
    if (!runState.taskId || !runState.loading) {
      setStatusMessage("")
      statusIndexRef.current = 0
      startTimeRef.current = null
      setElapsedTime(0)
      return
    }
    
    // Track start time when processing begins
    if (!startTimeRef.current) {
      startTimeRef.current = Date.now()
    }
    
    // Update elapsed time every second
    const timeInterval = setInterval(() => {
      if (startTimeRef.current) {
        const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000)
        setElapsedTime(elapsed)
      }
    }, 1000)
    
    // Show fake status messages during processing
    const statusInterval = setInterval(() => {
      if (statusIndexRef.current < STATUS_MESSAGES.length) {
        setStatusMessage(STATUS_MESSAGES[statusIndexRef.current])
        statusIndexRef.current++
      } else {
        // Cycle through messages
        statusIndexRef.current = Math.floor(Math.random() * STATUS_MESSAGES.length)
      }
    }, 3000) // Change message every 3 seconds

    const poll = async () => {
      const result = await pollResult(runState.taskId)
      if (result) {
        if (pollRef.current) clearInterval(pollRef.current)
        clearInterval(statusInterval)
        clearInterval(timeInterval)
        setStatusMessage("")
        setElapsedTime(0)
        startTimeRef.current = null
      }
    }
    poll()
    pollRef.current = setInterval(poll, POLL_INTERVAL)
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
      clearInterval(statusInterval)
      clearInterval(timeInterval)
    }
  }, [runState.taskId, runState.loading, pollResult])

  return (
    <div className="app">
      <header className="header">
        <h1>CI/CD Healing Agent</h1>
        <span className="badge">RIFT 2026 • AIML</span>
      </header>

      <main className="main">
        <InputSection />

        {runState.error && (
          <div className="error-banner">{runState.error}</div>
        )}

        {runState.loading && statusMessage && (
          <div className="status-message">
            <div>
              <span className="spinner" />
              {statusMessage}
            </div>
            {elapsedTime > 60 && (
              <div className="long-processing-warning">
                ⏱️ Large dataset detected — processing may take longer than usual. Please wait...
              </div>
            )}
          </div>
        )}

        {runState.result && (
          <>
            <RunSummary result={runState.result} />
            <ScoreBreakdown score={runState.result.score} />
            <FixesTable fixes={runState.result.fixes || []} />
            <Timeline timeline={runState.result.timeline || []} retryLimit={runState.result.retry_limit} />
            <DownloadResults result={runState.result} />
          </>
        )}
      </main>
    </div>
  )
}

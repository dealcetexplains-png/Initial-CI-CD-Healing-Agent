import React, { createContext, useContext, useState, useCallback } from 'react'

const AppContext = createContext(null)

const API_BASE =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.PROD
    ? 'https://initial-ci-cd-healing-agent-3.onrender.com/api'
    : '/api')

export function AppProvider({ children }) {
  const [runState, setRunState] = useState({
    loading: false,
    taskId: null,
    result: null,
    error: null,
  })

  const runAgent = useCallback(async (repoUrl, teamName, teamLeader) => {
    setRunState({ loading: true, taskId: null, result: null, error: null })
    try {
      const res = await fetch(`${API_BASE}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_url: repoUrl,
          team_name: teamName,
          team_leader: teamLeader,
        }),
      })
      let data
      try {
        data = await res.json()
      } catch (err) {
        // Backend returned non-JSON (often means API is down or crashed)
        throw new Error('Backend returned an invalid response. Is the API running on http://localhost:8000?')
      }
      if (!res.ok) throw new Error(data.detail || 'Failed to start agent')
      setRunState(s => ({ ...s, taskId: data.task_id }))
      return data.task_id
    } catch (err) {
      setRunState(s => ({ ...s, loading: false, error: err.message }))
      return null
    }
  }, [])

  const pollResult = useCallback(async (taskId) => {
    const res = await fetch(`${API_BASE}/result/${taskId}`)
    let data
    try {
      data = await res.json()
    } catch (err) {
      // If this happens once the run started, keep showing loading and surface a clear message
      throw new Error('Failed to read agent result (invalid JSON from backend). Check backend logs.')
    }
    if (data.status !== 'running' && !data.error) {
      setRunState(s => ({ ...s, loading: false, result: data }))
      return data
    }
    if (data.error) {
      setRunState(s => ({ ...s, loading: false, error: data.error, result: data }))
      return data
    }
    return null
  }, [])

  return (
    <AppContext.Provider value={{ runState, setRunState, runAgent, pollResult }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}

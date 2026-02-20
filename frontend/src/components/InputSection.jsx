import React, { useState } from 'react'
import { useApp } from '../context/AppContext'
import './InputSection.css'

export default function InputSection() {
  const { runState, runAgent } = useApp()
  const [repoUrl, setRepoUrl] = useState('')
  const [teamName, setTeamName] = useState('kyu nahi ho rahi padhai')
  const [teamLeader, setTeamLeader] = useState('Dornal Shivprasad')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!repoUrl.trim()) return
    await runAgent(repoUrl.trim(), teamName.trim(), teamLeader.trim())
  }

  return (
    <section className="input-section card">
      <h2>1. Input</h2>
      <div className="important-note">
        <strong>📌 Important Note:</strong> If the repository is owned by you, a branch will be created. 
        If the repository is not owned by you, a fork and branch will be created automatically.
      </div>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="repo">GitHub Repository URL</label>
          <input
            id="repo"
            type="url"
            placeholder="https://github.com/user/repo"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            disabled={runState.loading}
            required
          />
        </div>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="team">Team Name</label>
            <input
              id="team"
              type="text"
              placeholder="kyu nahi ho rahi padhai"
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              disabled={runState.loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="leader">Team Leader Name</label>
            <input
              id="leader"
              type="text"
              placeholder="Dornal Shivprasad"
              value={teamLeader}
              onChange={(e) => setTeamLeader(e.target.value)}
              disabled={runState.loading}
            />
          </div>
        </div>
        <button type="submit" className="btn-run" disabled={runState.loading}>
          {runState.loading ? (
            <>
              <span className="spinner" />
              Running Agent...
            </>
          ) : (
            'Run Agent'
          )}
        </button>
      </form>
    </section>
  )
}

import React from 'react'
import './RunSummary.css'

export default function RunSummary({ result }) {
  const passed = result.ci_status === 'PASSED'

  return (
    <section className="run-summary card">
      <h2>2. Run Summary</h2>
      <div className="summary-grid">
        <div className="summary-item">
          <span className="label">Repository</span>
          <span className="value mono">{result.repo_url}</span>
        </div>
        <div className="summary-item">
          <span className="label">Team</span>
          <span className="value">{result.team_name} / {result.team_leader}</span>
        </div>
        <div className="summary-item">
          <span className="label">Branch</span>
          <span className="value mono">{result.branch_name}</span>
        </div>
        <div className="summary-item">
          <span className="label">Failures</span>
          <span className="value">{result.total_failures_detected || 0}</span>
        </div>
        <div className="summary-item">
          <span className="label">Fixes Applied</span>
          <span className="value">{result.total_fixes_applied || 0}</span>
        </div>
        <div className="summary-item">
          <span className="label">Time</span>
          <span className="value">{result.total_time_seconds || 0}s</span>
        </div>
        {result.regressions_prevented > 0 && (
          <div className="summary-item">
            <span className="label">Regressions Prevented</span>
            <span className="value">{result.regressions_prevented}</span>
          </div>
        )}
      </div>
      <div className="status-row">
        <span className="label">CI/CD Status</span>
        <span className={`status-badge ${passed ? 'passed' : 'failed'}`}>
          {passed ? 'PASSED' : 'FAILED'}
        </span>
      </div>
      {result.github_ci && (
        <div className="status-row github-ci">
          <span className="label">GitHub Actions</span>
          <span className={`status-badge ${result.github_ci.status === 'success' ? 'passed' : result.github_ci.status === 'failure' ? 'failed' : 'neutral'}`}>
            {result.github_ci.status === 'success' ? 'PASSED' : result.github_ci.status === 'failure' ? 'FAILED' : result.github_ci.status || result.github_ci.message}
          </span>
          {result.github_ci.message && <span className="github-ci-msg">{result.github_ci.message}</span>}
        </div>
      )}
    </section>
  )
}

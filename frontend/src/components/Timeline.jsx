import React from 'react'
import './Timeline.css'

export default function Timeline({ timeline, retryLimit = 5 }) {
  if (!timeline || timeline.length === 0) {
    return (
      <section className="timeline card">
        <h2>5. CI/CD Status Timeline</h2>
        <p className="empty">No runs recorded.</p>
      </section>
    )
  }

  return (
    <section className="timeline card">
      <h2>5. CI/CD Status Timeline</h2>
      <div className="timeline-header">
        <span>Iterations: {timeline.length}/{retryLimit}</span>
      </div>
      <div className="timeline-list">
        {timeline.map((item, i) => (
          <div key={i} className="timeline-item">
            <div className="timeline-marker">
              <span className={`badge ${item.status === 'PASSED' ? 'passed' : 'failed'}`}>
                {item.status}
              </span>
            </div>
            <div className="timeline-content">
              <span>Iteration {item.iteration}</span>
              <span className="muted">{item.failures_count ?? 0} failures</span>
              {item.timestamp && (
                <span className="ts">{new Date(item.timestamp).toLocaleTimeString()}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

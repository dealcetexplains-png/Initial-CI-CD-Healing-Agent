import React from 'react'
import './ScoreBreakdown.css'

export default function ScoreBreakdown({ score }) {
  const s = score || { base: 100, speed_bonus: 0, efficiency_penalty: 0, total: 100 }
  const total = s.base + (s.speed_bonus || 0) - (s.efficiency_penalty || 0)
  const maxScore = 110
  const pct = Math.min(100, (total / maxScore) * 100)

  return (
    <section className="score-breakdown card">
      <h2>3. Score Breakdown</h2>
      <div className="score-items">
        <div className="score-item">
          <span>Base score</span>
          <span className="num">+{s.base}</span>
        </div>
        <div className="score-item">
          <span>Speed bonus (&lt;5 min)</span>
          <span className="num positive">+{s.speed_bonus || 0}</span>
        </div>
        <div className="score-item">
          <span>Efficiency penalty (&gt;20 commits)</span>
          <span className="num negative">−{s.efficiency_penalty || 0}</span>
        </div>
      </div>
      <div className="score-total">
        <span>Total</span>
        <span className="total-num">{total}</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
    </section>
  )
}

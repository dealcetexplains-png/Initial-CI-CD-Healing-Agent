import React from 'react'
import './FixesTable.css'

export default function FixesTable({ fixes }) {
  if (!fixes || fixes.length === 0) {
    return (
      <section className="fixes-table card">
        <h2>4. Fixes Applied</h2>
        <p className="empty">No fixes recorded.</p>
      </section>
    )
  }

  return (
    <section className="fixes-table card">
      <h2>4. Fixes Applied</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>File</th>
              <th>Bug Type</th>
              <th>Line</th>
              <th>Error</th>
              <th>Commit Message</th>
              <th>AI Providers</th>
              <th>Status</th>
              <th>Debug</th>
            </tr>
          </thead>
          <tbody>
            {fixes.map((fix, i) => {
              const d = fix.debug || {}
              const rawStr = d.raw && Object.keys(d.raw).length
                ? Object.entries(d.raw).map(([k, v]) => `${k}:${v}`).join(' ')
                : ''
              const errorLine = fix.line ? `line:${fix.line}` : ''
              const debugStr = [
                errorLine,
                d.strategy || '—',
                d.content_len != null ? `len=${d.content_len}` : '',
                d.ast_error ? `ast=${d.ast_error}` : '',
                d.exception ? `err=${String(d.exception).slice(0, 40)}…` : '',
                rawStr,
              ].filter(Boolean).join(' | ')
              const errMsg = fix.error_message || d.message || ''
              // Format error display: [file] — Line [X]: [error message]
              const errorDisplay = fix.line && errMsg
                ? `${fix.file} — Line ${fix.line}: ${errMsg}`
                : errMsg || '—'
              // Show ALL line numbers where errors exist
              const allLines = fix.all_lines && fix.all_lines.length > 1 
                ? fix.all_lines.join(', ') 
                : (fix.line ?? '—')
              const lineDisplay = fix.all_lines && fix.all_lines.length > 1
                ? `${fix.line} (all: ${allLines})`
                : allLines
              return (
              <tr key={i}>
                <td className="mono">{fix.file}</td>
                <td><span className={`bug-type ${(fix.bug_type || '').toLowerCase()}`}>{fix.bug_type || '—'}</span></td>
                <td className="line-cell" title={fix.all_lines ? `All error lines: ${fix.all_lines.join(', ')}` : ''}>{lineDisplay}</td>
                <td className="error-cell" title={errMsg}>{errorDisplay}</td>
                <td className="commit-msg">{fix.commit_message}</td>
                <td className="providers">{fix.providers_used?.length ? fix.providers_used.join(' + ') : 'Ollama'}</td>
                <td>
                  <span className="status-dot fixed">
                    ✓ Fixed
                  </span>
                </td>
                <td className="debug-cell" title={JSON.stringify(d)}>{debugStr || '—'}</td>
              </tr>
            )})}
          </tbody>
        </table>
      </div>
    </section>
  )
}

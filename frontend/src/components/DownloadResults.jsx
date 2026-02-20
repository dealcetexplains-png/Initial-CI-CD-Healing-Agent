import React from 'react'
import './DownloadResults.css'

export default function DownloadResults({ result }) {
  const handleDownload = () => {
    if (!result) return
    
    // Convert result to JSON string
    const jsonStr = JSON.stringify(result, null, 2)
    const blob = new Blob([jsonStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    
    // Create download link
    const link = document.createElement('a')
    link.href = url
    link.download = 'results.json'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <section className="download-results card">
      <button onClick={handleDownload} className="btn-download">
        <span>📥</span>
        Download results.json
      </button>
    </section>
  )
}

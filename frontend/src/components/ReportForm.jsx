import React, { useState } from 'react'
import axios from 'axios'

export default function ReportForm() {
  const [summary, setSummary] = useState('')
  const [category, setCategory] = useState('phishing')
  const [resp, setResp] = useState(null)
  const [error, setError] = useState(null)

  const submit = async (e) => {
    e.preventDefault()
    setError(null)
    setResp(null)
    try {
      const r = await axios.post('/api/reports', { summary, category })
      setResp(r.data)
    } catch (err) {
      setError(err?.response?.data || 'Error submitting report')
    }
  }

  return (
    <form onSubmit={submit}>
      <label>Category</label><br/>
      <select value={category} onChange={e => setCategory(e.target.value)}>
        <option value="phishing">Phishing</option>
        <option value="scam">Scam</option>
        <option value="malware">Malware</option>
        <option value="harassment">Harassment</option>
      </select>
      <br/><br/>
      <label>Summary</label><br/>
      <textarea
        rows={6}
        style={{ width: '100%' }}
        placeholder="Describe what happened (no personal info)."
        value={summary}
        onChange={e => setSummary(e.target.value)}
      />
      <br/>
      <button type="submit">Submit</button>

      {error && <p style={{ color: 'crimson' }}>{String(error)}</p>}
      {resp && (
        <div style={{ marginTop: 12, background: '#f7f7f7', padding: 8, borderRadius: 6 }}>
          <p><b>Report ID:</b> {resp.id}</p>
          <p><b>Score:</b> {resp.score}</p>
          <p><b>Reasons:</b> {resp.reasons.join(', ') || '—'}</p>
          <p><b>Receipt:</b> <code style={{ fontSize: 12 }}>{resp.receipt}</code></p>
          <p><b>Created At:</b> {resp.created_at}</p>
        </div>
      )}
    </form>
  )
}
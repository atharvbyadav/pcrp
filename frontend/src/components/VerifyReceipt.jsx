import React, { useState } from 'react'
import axios from 'axios'

export default function VerifyReceipt() {
  const [reportId, setReportId] = useState('')
  const [receipt, setReceipt] = useState('')
  const [result, setResult] = useState(null)

  const verify = async (e) => {
    e.preventDefault()
    const url = receipt
      ? `/api/receipts/${encodeURIComponent(reportId)}?receipt=${encodeURIComponent(receipt)}`
      : `/api/receipts/${encodeURIComponent(reportId)}`
    const r = await axios.get(url)
    setResult(r.data)
  }

  return (
    <form onSubmit={verify}>
      <label>Report ID</label><br/>
      <input style={{ width: '100%' }} value={reportId} onChange={e => setReportId(e.target.value)} /><br/><br/>
      <label>Receipt (optional)</label><br/>
      <input style={{ width: '100%' }} value={receipt} onChange={e => setReceipt(e.target.value)} /><br/><br/>
      <button type="submit">Verify</button>
      {result && (
        <div style={{ marginTop: 12, background: '#f7f7f7', padding: 8, borderRadius: 6 }}>
          <p><b>Exists:</b> {String(result.exists)}</p>
          {"receipt_matches" in result && result.receipt_matches !== null && (
            <p><b>Receipt Matches:</b> {String(result.receipt_matches)}</p>
          )}
          {result.expected_receipt && (
            <p><b>Expected Receipt:</b> <code style={{ fontSize: 12 }}>{result.expected_receipt}</code></p>
          )}
        </div>
      )}
    </form>
  )
}
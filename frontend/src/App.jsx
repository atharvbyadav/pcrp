import React, { useEffect, useState } from 'react'
import ReportForm from './components/ReportForm.jsx'
import VerifyReceipt from './components/VerifyReceipt.jsx'
import axios from 'axios'

export default function App() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    axios.get('/api/dashboard/stats').then(res => setStats(res.data))
  }, [])

  return (
    <div style={{ fontFamily: 'system-ui, Arial, sans-serif', padding: 16, maxWidth: 960, margin: '0 auto' }}>
      <h1>PCRP — Public Cyber Incident Reporting Portal</h1>
      <p style={{ color: '#555' }}>
        Privacy-first reporting. Get a verifiable receipt. Help detect campaigns.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
          <h2>Report an Incident</h2>
          <ReportForm />
        </div>
        <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
          <h2>Verify a Receipt</h2>
          <VerifyReceipt />
        </div>
      </div>

      <div style={{ marginTop: 24, border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
        <h2>Dashboard</h2>
        {stats ? (
          <div>
            <p><b>Total Reports:</b> {stats.total_reports}</p>
            <ul>
              {stats.by_category.map((c) => (
                <li key={c.category}>{c.category}: {c.count}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p>Loading stats…</p>
        )}
      </div>
    </div>
  )
}
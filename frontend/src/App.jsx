// frontend/src/App.jsx
import { useState, useEffect, useCallback, lazy, Suspense } from 'react'
import { listCases, getStats, checkHealth } from './api/client'
import StatsBar from './components/StatsBar'
import SubmitForm from './components/SubmitForm'
import CaseTable from './components/CaseTable'

const CaseDetailModal = lazy(() => import('./components/CaseDetailModal'))
import ErrorBoundary from './components/ErrorBoundary'

export default function App() {
  const [cases, setCases] = useState([])
  const [stats, setStats] = useState(null)
  const [selected, setSelected] = useState(null)
  const [healthy, setHealthy] = useState(null)

  const refresh = useCallback(async () => {
    try {
      const [c, s] = await Promise.all([listCases(100), getStats()])
      setCases(c.cases || [])
      setStats(s)
      setHealthy(true)
    } catch {
      setHealthy(false)
    }
  }, [])

  useEffect(() => {
    checkHealth().then(() => setHealthy(true)).catch(() => setHealthy(false))
    refresh()
    const id = setInterval(refresh, 3000)
    return () => clearInterval(id)
  }, [refresh])

  useEffect(() => {
    if (selected) {
      const updated = cases.find(c => c.record_id === selected.record_id)
      if (updated) setSelected(updated)
    }
  }, [cases])

  return (
    <div className="min-h-screen bg-gray-50">
      {selected && (
  <ErrorBoundary onClose={() => setSelected(null)}>
    <Suspense fallback={
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-6 text-sm text-gray-500">
          Loading case detail...
        </div>
      </div>
    }>
      <CaseDetailModal
        caseData={selected}
        onClose={() => setSelected(null)}
        onOverride={refresh}
      />
    </Suspense>
  </ErrorBoundary>
)}

      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-screen-xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-lg font-bold text-gray-900">KYC & Identity Risk Platform</h1>
            <p className="text-xs text-gray-400 mt-0.5">OCR · Sanctions/PEP Screening · XGBoost · SHAP</p>
          </div>
          <span className={`text-xs px-3 py-1 rounded-full flex items-center gap-1.5
            ${healthy === true ? 'bg-green-50 text-green-700' : healthy === false ? 'bg-red-50 text-red-600' : 'bg-gray-100 text-gray-400'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${healthy === true ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
            {healthy === true ? 'API Connected' : healthy === false ? 'API Unreachable' : 'Connecting…'}
          </span>
        </div>
      </header>

      <main className="max-w-screen-xl mx-auto px-6 py-6">
        <StatsBar stats={stats} />
        <SubmitForm onSubmitted={refresh} />

        <div className="flex justify-between items-center mb-3">
          <h2 className="font-semibold text-gray-700">
            Case Queue <span className="text-sm font-normal text-gray-400">({cases.length})</span>
          </h2>
          <span className="text-xs text-gray-400">Click a row to review</span>
        </div>

        <CaseTable cases={cases} onSelect={setSelected} />
      </main>
    </div>
  )
}
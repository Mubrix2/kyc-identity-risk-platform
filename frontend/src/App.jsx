// frontend/src/App.jsx
import { useState, useEffect, useCallback, lazy, Suspense } from 'react'
import { listCases, getStats, checkHealth } from './api/client'
import StatsBar from './components/StatsBar'
import SubmitForm from './components/SubmitForm'
import CaseList from './components/CaseList'
import CasePanel from './components/CasePanel'
import ErrorBoundary from './components/ErrorBoundary'

export default function App() {
  const [cases, setCases]       = useState([])
  const [stats, setStats]       = useState(null)
  const [selected, setSelected] = useState(null)
  const [healthy, setHealthy]   = useState(null)
  const [view, setView]         = useState('queue') // 'queue' | 'submit'

  const refresh = useCallback(async () => {
    try {
      const [c, s] = await Promise.all([listCases(100), getStats()])
      setCases(c.cases || [])
      setStats(s)
      setHealthy(true)
    } catch { setHealthy(false) }
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
    <div className="min-h-screen bg-slate-50 flex flex-col">

      {/* Header */}
      <header className="bg-indigo-900 text-white px-6 py-3 flex
        justify-between items-center shadow-lg">
        <div>
          <h1 className="text-base font-bold tracking-wide">
            KYC Compliance Platform
          </h1>
          <p className="text-xs text-indigo-300 mt-0.5">
            OCR · Sanctions/PEP · XGBoost · SHAP · PostgreSQL Audit
          </p>
        </div>
        <div className="flex items-center gap-4">
          <span className={`text-xs px-3 py-1 rounded-full flex items-center
            gap-1.5 ${healthy ? 'bg-green-500/20 text-green-300'
            : 'bg-red-500/20 text-red-300'}`}>
            <span className={`w-1.5 h-1.5 rounded-full
              ${healthy ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}/>
            {healthy ? 'Connected' : 'Offline'}
          </span>
        </div>
      </header>

      {/* Stats */}
      <div className="px-6 py-3 bg-white border-b border-gray-200">
        <StatsBar stats={stats} />
      </div>

      {/* Nav */}
      <div className="px-6 bg-white border-b border-gray-100">
        <div className="flex gap-1">
          {[['queue', '📋 Case Queue'], ['submit', '➕ New Application']].map(([key, label]) => (
            <button key={key} onClick={() => setView(key)}
              className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors
                ${view === key
                  ? 'border-indigo-600 text-indigo-700'
                  : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Main */}
      <div className="flex flex-1 overflow-hidden">
        {view === 'submit' ? (
          <div className="flex-1 p-6 overflow-y-auto">
            <SubmitForm onSubmitted={() => { refresh(); setView('queue') }} />
          </div>
        ) : (
          <>
            {/* Left — case list */}
            <div className="w-80 border-r border-gray-200 bg-white
              overflow-y-auto flex-shrink-0">
              <div className="p-3 border-b border-gray-100 bg-gray-50">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Case Queue ({cases.length})
                </p>
              </div>
              <CaseList cases={cases} selected={selected} onSelect={setSelected} />
            </div>

            {/* Right — case detail inline */}
            <div className="flex-1 overflow-y-auto p-6">
              {selected ? (
                <ErrorBoundary onClose={() => setSelected(null)}>
                  <CasePanel caseData={selected} onOverride={refresh} />
                </ErrorBoundary>
              ) : (
                <div className="flex flex-col items-center justify-center
                  h-full text-gray-400">
                  <span className="text-5xl mb-4">🔍</span>
                  <p className="text-lg font-medium">Select a case to review</p>
                  <p className="text-sm mt-1">
                    Cases requiring attention are highlighted
                  </p>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
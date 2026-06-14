// frontend/src/components/CaseDetailModal.jsx
import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer, ReferenceLine } from 'recharts'
import DecisionBadge from './DecisionBadge'
import { overrideDecision } from '../api/client'

export default function CaseDetailModal({ caseData: c, onClose, onOverride }) {
  if (!c) return null

  const [reason, setReason] = useState('')
  const [reviewer, setReviewer] = useState('')
  const [overriding, setOverriding] = useState(false)

  useEffect(() => {
    const fn = e => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', fn)
    return () => window.removeEventListener('keydown', fn)
  }, [onClose])

  const chartData = (c.top_reasons || [])
    .filter(r => r && typeof r.shap_value === 'number' && isFinite(r.shap_value))
    .map(r => ({
      name: r.description.length > 30 ? r.description.slice(0, 30) + '…' : r.description,
      value: r.shap_value,
      direction: r.direction,
    }))

  const fv = c.field_validation || {}
  const screening = c.screening || {}

  const submitOverride = async (newDecision) => {
    if (!reason || !reviewer) { alert('Enter reviewer name and reason'); return }
    setOverriding(true)
    try {
      await overrideDecision({ record_id: c.record_id, new_decision: newDecision, reason, reviewer })
      onOverride?.()
      onClose()
    } catch (e) {
      alert(e.message)
    } finally {
      setOverriding(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">

        <div className="flex justify-between items-start p-5 border-b border-gray-100 sticky top-0 bg-white">
          <div>
            <h2 className="font-bold text-gray-900">KYC Case Detail</h2>
            <p className="text-xs text-gray-400 font-mono mt-0.5">{c.record_id}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-xl w-8 h-8 rounded-lg hover:bg-gray-100">✕</button>
        </div>

        <div className="p-5 space-y-5">

          {/* Summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Decision</p>
              <DecisionBadge decision={c.decision} />
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Risk Probability</p>
              <p className="text-xl font-bold">{(c.risk_probability * 100).toFixed(1)}%</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Risk Tier</p>
              <p className="text-sm font-semibold">{c.risk_tier}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Processing</p>
              <p className="text-sm font-semibold">{c.processing_ms?.toFixed(1)} ms</p>
            </div>
          </div>

          {/* Declared vs Extracted */}
          <div>
            <p className="text-xs font-semibold text-gray-700 mb-2">Declared vs. Document-Extracted</p>
            <div className="bg-gray-50 rounded-lg p-3 text-xs space-y-1">
              <div className="flex justify-between">
                <span>Name match score</span>
                <span className={fv.name_match_score < 0.8 ? 'text-red-600 font-semibold' : 'text-green-600'}>
                  {(fv.name_match_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span>DOB mismatch</span>
                <span className={fv.dob_mismatch ? 'text-red-600 font-semibold' : 'text-green-600'}>
                  {fv.dob_mismatch ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>ID number mismatch</span>
                <span className={fv.id_number_mismatch ? 'text-red-600 font-semibold' : 'text-green-600'}>
                  {fv.id_number_mismatch ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          </div>

          {/* Sanctions/PEP evidence */}
          {(screening.sanctions?.is_match || screening.pep?.is_match) && (
            <div>
              <p className="text-xs font-semibold text-gray-700 mb-2">Screening Evidence</p>
              <div className="space-y-2">
                {screening.sanctions?.is_match && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-xs text-red-800">
                    <strong>Sanctions match:</strong> {screening.sanctions.matched_name} ({screening.sanctions.program}) — {(screening.sanctions.score * 100).toFixed(1)}% similarity
                  </div>
                )}
                {screening.pep?.is_match && (
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 text-xs text-orange-800">
                    <strong>PEP match:</strong> {screening.pep.matched_name} ({screening.pep.category}) — {(screening.pep.score * 100).toFixed(1)}% similarity
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Triggered rules */}
          {(c.triggered_rules || []).length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-700 mb-2">Rules / Override History</p>
              {c.triggered_rules.map((r, i) => (
                <div key={i} className="text-xs bg-amber-50 border border-amber-200 text-amber-800 rounded px-3 py-1.5 mb-1">⚡ {r}</div>
              ))}
            </div>
          )}

          {/* SHAP chart */}
          {chartData.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-700 mb-2">SHAP Risk Factors</p>
              <div className="bg-gray-50 rounded-lg p-4">
                <ResponsiveContainer width="100%" height={chartData.length * 40 + 20}>
                  <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 24, bottom: 4, left: 8 }}>
                    <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={v => v.toFixed(2)} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 10 }} width={190} />
                    <ReferenceLine x={0} stroke="#d1d5db" />
                    <Tooltip formatter={(v) => v.toFixed(4)} />
                    <Bar dataKey="value" radius={[0, 3, 3, 0]} maxBarSize={20}>
                      {chartData.map((e, i) => (
                        <Cell key={i} fill={e.direction === 'increased_risk' ? '#ef4444' : '#22c55e'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Override panel */}
          <div className="border-t border-gray-100 pt-4">
            <p className="text-xs font-semibold text-gray-700 mb-2">Reviewer Override</p>
            <div className="grid grid-cols-2 gap-2 mb-2">
              <input placeholder="Reviewer name" value={reviewer} onChange={e => setReviewer(e.target.value)}
                className="text-sm border border-gray-200 rounded px-2 py-1.5" />
              <input placeholder="Reason (min 10 chars)" value={reason} onChange={e => setReason(e.target.value)}
                className="text-sm border border-gray-200 rounded px-2 py-1.5" />
            </div>
            <div className="flex gap-2">
              {['APPROVE', 'REVIEW', 'REJECT'].map(d => (
                <button key={d} disabled={overriding || d === c.decision} onClick={() => submitOverride(d)}
                  className="px-3 py-1.5 text-xs border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-40">
                  Set {d}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
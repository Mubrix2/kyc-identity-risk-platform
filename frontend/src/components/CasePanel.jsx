// frontend/src/components/CasePanel.jsx
import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
         ResponsiveContainer, ReferenceLine } from 'recharts'
import DecisionBadge from './DecisionBadge'
import { overrideDecision } from '../api/client'

export default function CasePanel({ caseData: c, onOverride }) {
  const [reason, setReason]     = useState('')
  const [reviewer, setReviewer] = useState('')
  const [overriding, setOverriding] = useState(false)

  if (!c) return null

  const fv       = c.field_validation || {}
  const screening = c.screening || {}

  const chartData = (c.top_reasons || [])
    .filter(r => r && typeof r.shap_value === 'number' && isFinite(r.shap_value))
    .map(r => ({
      name: r.description?.length > 28
        ? r.description.slice(0, 28) + '…' : r.description,
      value: r.shap_value,
      direction: r.direction,
    }))

  const submitOverride = async (decision) => {
    if (!reason || !reviewer) { alert('Enter name and reason'); return }
    setOverriding(true)
    try {
      await overrideDecision({
        record_id: c.record_id, new_decision: decision,
        reason, reviewer,
      })
      onOverride?.()
    } catch (e) { alert(e.message) }
    finally { setOverriding(false) }
  }

  return (
    <div className="max-w-3xl">
      {/* Case header */}
      <div className="flex justify-between items-start mb-5">
        <div>
          <h2 className="text-xl font-bold text-gray-900">{c.declared_name}</h2>
          <p className="text-xs font-mono text-gray-400 mt-0.5">{c.record_id}</p>
        </div>
        <DecisionBadge decision={c.decision} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">

        {/* Summary */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <p className="text-xs font-semibold text-gray-500 uppercase
            tracking-wide mb-3">Risk Summary</p>
          <div className="grid grid-cols-2 gap-3">
            {[
              ['Risk Probability', `${(c.risk_probability*100).toFixed(1)}%`],
              ['Risk Tier', c.risk_tier || '—'],
              ['Processing', `${c.processing_ms?.toFixed(0)}ms`],
              ['Requires EDD', c.requires_edd ? '⚠ Yes' : 'No'],
            ].map(([label, val]) => (
              <div key={label} className="bg-gray-50 rounded-lg p-2.5">
                <p className="text-xs text-gray-400 mb-0.5">{label}</p>
                <p className="text-sm font-semibold">{val}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Face verification frame */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex justify-between items-center mb-3">
            <p className="text-xs font-semibold text-gray-500 uppercase
              tracking-wide">Biometric Verification</p>
            <span className="text-xs px-2 py-0.5 bg-indigo-100 text-indigo-700
              rounded-full font-medium">Local Only · Beta</span>
          </div>
          <div className="border-2 border-dashed border-gray-200 rounded-xl
            h-32 flex flex-col items-center justify-center bg-gray-50">
            <span className="text-3xl mb-1.5">📷</span>
            <p className="text-xs font-medium text-gray-500">
              Face Verification
            </p>
            <p className="text-xs text-gray-400 mt-0.5 text-center px-4">
              {c.face_verification
                ? `Match score: ${(c.face_verification.face_match_score * 100).toFixed(1)}%`
                : 'Not performed — requires local deployment with face_recognition enabled'}
            </p>
          </div>
        </div>
      </div>

      {/* Document comparison */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
        <p className="text-xs font-semibold text-gray-500 uppercase
          tracking-wide mb-3">Document Validation</p>
        <div className="grid grid-cols-3 gap-3 text-sm">
          <div>
            <p className="text-xs text-gray-400 mb-1">Name Match</p>
            <div className={`flex items-center gap-1.5 font-semibold
              ${fv.name_match_score >= 0.85 ? 'text-green-600' : 'text-red-600'}`}>
              <span>{fv.name_match_score >= 0.85 ? '✓' : '✗'}</span>
              {((fv.name_match_score || 0) * 100).toFixed(0)}%
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-1">Date of Birth</p>
            <div className={`flex items-center gap-1.5 font-semibold
              ${!fv.dob_mismatch ? 'text-green-600' : 'text-red-600'}`}>
              <span>{!fv.dob_mismatch ? '✓' : '✗'}</span>
              {fv.dob_mismatch ? 'Mismatch' : 'Match'}
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-400 mb-1">ID Number</p>
            <div className={`flex items-center gap-1.5 font-semibold
              ${!fv.id_number_mismatch ? 'text-green-600' : 'text-red-600'}`}>
              <span>{!fv.id_number_mismatch ? '✓' : '✗'}</span>
              {fv.id_number_mismatch ? 'Mismatch' : 'Match'}
            </div>
          </div>
        </div>
      </div>

      {/* Sanctions evidence */}
      {(screening.sanctions?.is_match || screening.pep?.is_match) && (
        <div className="mb-4 space-y-2">
          {screening.sanctions?.is_match && (
            <div className="bg-red-50 border border-red-200 rounded-xl
              p-3 text-xs text-red-800">
              <strong>🚫 Sanctions Match:</strong> {screening.sanctions.matched_name}
              ({screening.sanctions.program}) —{' '}
              {(screening.sanctions.score * 100).toFixed(1)}% similarity
            </div>
          )}
          {screening.pep?.is_match && (
            <div className="bg-orange-50 border border-orange-200 rounded-xl
              p-3 text-xs text-orange-800">
              <strong>⚠ PEP Match:</strong> {screening.pep.matched_name}
              ({screening.pep.category}) —{' '}
              {(screening.pep.score * 100).toFixed(1)}% similarity
            </div>
          )}
        </div>
      )}

      {/* Rules */}
      {(c.triggered_rules || []).length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-500 uppercase
            tracking-wide mb-2">Rules Triggered</p>
          {c.triggered_rules.map((r, i) => (
            <div key={i} className="text-xs bg-amber-50 border border-amber-200
              text-amber-800 rounded-lg px-3 py-1.5 mb-1">⚡ {r}</div>
          ))}
        </div>
      )}

      {/* SHAP chart */}
      {chartData.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
          <p className="text-xs font-semibold text-gray-500 uppercase
            tracking-wide mb-3">Risk Factor Analysis (SHAP)</p>
          <ResponsiveContainer width="100%" height={chartData.length * 40 + 20}>
            <BarChart data={chartData} layout="vertical"
              margin={{ top: 4, right: 24, bottom: 4, left: 8 }}>
              <XAxis type="number" tick={{ fontSize: 10 }}
                tickFormatter={v => v.toFixed(2)} />
              <YAxis type="category" dataKey="name"
                tick={{ fontSize: 10 }} width={200} />
              <ReferenceLine x={0} stroke="#d1d5db" />
              <Tooltip formatter={v => v.toFixed(4)} />
              <Bar dataKey="value" radius={[0, 3, 3, 0]} maxBarSize={18}>
                {chartData.map((e, i) => (
                  <Cell key={i}
                    fill={e.direction === 'increased_risk' ? '#ef4444' : '#22c55e'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Reviewer override */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <p className="text-xs font-semibold text-gray-500 uppercase
          tracking-wide mb-3">Compliance Review</p>
        <div className="grid grid-cols-2 gap-2 mb-3">
          <input placeholder="Reviewer name"
            value={reviewer} onChange={e => setReviewer(e.target.value)}
            className="text-sm border border-gray-200 rounded-lg px-3 py-2" />
          <input placeholder="Reason for override (min 10 chars)"
            value={reason} onChange={e => setReason(e.target.value)}
            className="text-sm border border-gray-200 rounded-lg px-3 py-2" />
        </div>
        <div className="flex gap-2">
          {['APPROVE', 'REVIEW', 'REJECT'].map(d => (
            <button key={d} disabled={overriding || d === c.decision}
              onClick={() => submitOverride(d)}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg border
                transition-colors disabled:opacity-40
                ${d === 'APPROVE' ? 'border-green-300 text-green-700 hover:bg-green-50' :
                  d === 'REVIEW'  ? 'border-yellow-300 text-yellow-700 hover:bg-yellow-50' :
                  'border-red-300 text-red-700 hover:bg-red-50'}`}>
              Set {d}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
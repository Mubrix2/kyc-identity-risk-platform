// frontend/src/components/CaseTable.jsx
import DecisionBadge from './DecisionBadge'

export default function CaseTable({ cases, onSelect }) {
  if (!cases.length) {
    return (
      <div className="text-center py-16 text-gray-400">
        <p className="text-lg font-medium">No cases yet</p>
        <p className="text-sm mt-1">Submit an application above to begin</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-gray-50 border-b border-gray-100">
            {['Record ID', 'Declared Name', 'Decision', 'Risk %', 'Tier', 'EDD', 'Rules', 'ms'].map(h => (
              <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {cases.map(c => {
            const rowBg =
              c.decision === 'REJECT' ? 'bg-red-50 hover:bg-red-100' :
              c.decision === 'REVIEW' ? 'bg-yellow-50 hover:bg-yellow-100' :
              'bg-white hover:bg-gray-50'

            return (
              <tr key={c.record_id} onClick={() => onSelect(c)}
                className={`border-b border-gray-100 cursor-pointer transition-colors ${rowBg}`}>
                <td className="px-4 py-3 font-mono text-xs text-gray-500">{c.record_id}</td>
                <td className="px-4 py-3 text-gray-700">{c.declared_name}</td>
                <td className="px-4 py-3"><DecisionBadge decision={c.decision} /></td>
                <td className="px-4 py-3 text-right">{(c.risk_probability * 100).toFixed(1)}%</td>
                <td className="px-4 py-3 text-xs text-gray-500">{c.risk_tier}</td>
                <td className="px-4 py-3 text-center">
                  {c.requires_edd ? <span className="text-orange-600 text-xs">⚠ EDD</span> : <span className="text-gray-300 text-xs">—</span>}
                </td>
                <td className="px-4 py-3 text-xs text-gray-500">{(c.triggered_rules || []).length || '—'}</td>
                <td className="px-4 py-3 text-right text-xs text-gray-400">{c.processing_ms?.toFixed(0)}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
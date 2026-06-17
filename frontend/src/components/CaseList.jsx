// frontend/src/components/CaseList.jsx
import DecisionBadge from './DecisionBadge'

export default function CaseList({ cases, selected, onSelect }) {
  if (!cases.length) {
    return (
      <div className="p-6 text-center text-gray-400 text-sm">
        No cases yet
      </div>
    )
  }

  return (
    <div className="divide-y divide-gray-100">
      {cases.map(c => {
        const isSelected = selected?.record_id === c.record_id
        const borderColour =
          c.decision === 'REJECT' ? 'border-l-red-500' :
          c.decision === 'REVIEW' ? 'border-l-yellow-400' :
          'border-l-green-400'

        return (
          <div key={c.record_id} onClick={() => onSelect(c)}
            className={`p-3 cursor-pointer border-l-4 transition-colors
              ${borderColour}
              ${isSelected ? 'bg-indigo-50' : 'hover:bg-gray-50'}`}>
            <div className="flex justify-between items-start mb-1">
              <p className="text-sm font-semibold text-gray-800 truncate">
                {c.declared_name}
              </p>
              <DecisionBadge decision={c.decision} />
            </div>
            <p className="text-xs font-mono text-gray-400">
              {c.record_id}
            </p>
            <div className="flex gap-2 mt-1.5 text-xs text-gray-500">
              <span>{(c.risk_probability * 100).toFixed(1)}% risk</span>
              {c.requires_edd && (
                <span className="text-orange-600 font-semibold">⚠ EDD</span>
              )}
              {(c.triggered_rules || []).length > 0 && (
                <span className="text-red-600">
                  {c.triggered_rules.length} rule{c.triggered_rules.length > 1 ? 's' : ''}
                </span>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
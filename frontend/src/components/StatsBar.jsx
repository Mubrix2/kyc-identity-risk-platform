// frontend/src/components/StatsBar.jsx
export default function StatsBar({ stats }) {
  const s = stats || {}
  const cards = [
    { label: 'Total Cases', value: s.total ?? 0, colour: 'text-blue-700', bg: 'bg-blue-50' },
    { label: 'Approved',    value: s.approve ?? 0, colour: 'text-green-700', bg: 'bg-green-50' },
    { label: 'Review',      value: s.review ?? 0, colour: 'text-yellow-700', bg: 'bg-yellow-50' },
    { label: 'Rejected',    value: s.reject ?? 0, colour: 'text-red-700', bg: 'bg-red-50' },
    { label: 'Requires EDD', value: s.requires_edd ?? 0, colour: 'text-orange-700', bg: 'bg-orange-50' },
    { label: 'Avg Latency', value: `${s.avg_processing_ms ?? 0} ms`, colour: 'text-gray-700', bg: 'bg-gray-50' },
  ]
  return (
    <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-6">
      {cards.map(c => (
        <div key={c.label} className={`${c.bg} rounded-lg p-4 border border-gray-100`}>
          <p className="text-xs text-gray-500 mb-1">{c.label}</p>
          <p className={`text-2xl font-bold ${c.colour}`}>{c.value}</p>
        </div>
      ))}
    </div>
  )
}
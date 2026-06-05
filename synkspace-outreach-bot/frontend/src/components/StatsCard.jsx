const colorMap = {
  indigo: 'from-brand-500 to-brand-600',
  emerald: 'from-emerald-500 to-emerald-600',
  rose: 'from-rose-500 to-rose-600',
  amber: 'from-amber-500 to-amber-600',
}

export default function StatsCard({ title, value, subtitle, icon, color = 'indigo' }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{value}</p>
          {subtitle && (
            <p className="mt-1 text-xs text-slate-400">{subtitle}</p>
          )}
        </div>
        <div
          className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${colorMap[color]} text-white shadow-sm`}
        >
          {icon}
        </div>
      </div>
    </div>
  )
}

import Dashboard from '../components/Dashboard'

export default function Home() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">
          Overview of your creator outreach performance
        </p>
      </div>
      <Dashboard />
    </div>
  )
}

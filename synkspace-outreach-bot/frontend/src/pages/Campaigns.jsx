import { useEffect, useState } from 'react'
import CampaignForm from '../components/CampaignForm'
import { getCampaigns } from '../api/axios'

export default function Campaigns() {
  const [campaigns, setCampaigns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchCampaigns = async () => {
    try {
      setLoading(true)
      setError(null)
      const res = await getCampaigns()
      setCampaigns(res.data.campaigns)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCampaigns()
  }, [])

  const statusColors = {
    draft: 'bg-slate-100 text-slate-600',
    sending: 'bg-amber-100 text-amber-700',
    completed: 'bg-emerald-100 text-emerald-700',
  }

  const templateLabels = {
    founding_creator: 'Founding Creator',
    follow_up: 'Follow Up',
    brand_invite: 'Brand Invite',
    event_invite: 'Event Invite',
    custom: 'Custom',
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Campaigns</h1>
        <p className="mt-1 text-sm text-slate-500">
          Create personalized email campaigns and send them to your creators
        </p>
      </div>

      <div className="grid gap-8 xl:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-6 text-lg font-semibold text-slate-900">New Campaign</h2>
          <CampaignForm onSuccess={fetchCampaigns} />
        </div>

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-6 py-4">
            <h2 className="text-lg font-semibold text-slate-900">Campaign History</h2>
          </div>

          {loading ? (
            <div className="flex h-48 items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
            </div>
          ) : error ? (
            <div className="p-6 text-sm text-rose-600">{error}</div>
          ) : campaigns.length === 0 ? (
            <div className="p-6 text-center text-sm text-slate-400">
              No campaigns yet. Create your first one!
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {campaigns.map((c) => (
                <div key={c._id} className="px-6 py-4 hover:bg-slate-50">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-medium text-slate-900">{c.name}</p>
                      <p className="mt-0.5 text-sm text-slate-500">{c.subject}</p>
                      {c.template_type && (
                        <p className="mt-0.5 text-xs text-brand-600">
                          {templateLabels[c.template_type] || c.template_type}
                        </p>
                      )}
                    </div>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColors[c.status] || statusColors.draft}`}
                    >
                      {c.status}
                    </span>
                  </div>
                  <div className="mt-2 flex gap-4 text-xs text-slate-400">
                    <span>Sent: {c.sent_count}</span>
                    <span>Failed: {c.failed_count}</span>
                    <span>Total: {c.total_recipients}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

import { useEffect, useState } from 'react'
import { getStats, getEmailLogs } from '../api/axios'
import StatsCard from './StatsCard'

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_creators: 0,
    emails_sent: 0,
    failed_emails: 0,
    open_rate: 0,
  })

  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        setError(null)

        const [statsRes, logsRes] = await Promise.all([
          getStats(),
          getEmailLogs(),
        ])

        console.log("Dashboard stats:", statsRes.data)

        setStats({
          total_creators:
            statsRes.data.total_creators ??
            statsRes.data.total ??
            0,

          emails_sent:
            statsRes.data.emails_sent ??
            0,

          failed_emails:
            statsRes.data.failed_emails ??
            0,

          open_rate:
            statsRes.data.open_rate ??
            0,
        })

        setLogs(logsRes.data.logs || [])

      } catch (err) {
        console.error(err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])


  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    )
  }


  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-700">
        Failed loading dashboard: {error}
      </div>
    )
  }


  return (
    <div className="space-y-8">


      {/* STATS CARDS */}

      <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">


        <StatsCard
          title="Total Creators"
          value={stats.total_creators}
          subtitle="In your database"
          color="indigo"
          icon={
            <span>
              👥
            </span>
          }
        />


        <StatsCard
          title="Emails Sent"
          value={stats.emails_sent}
          subtitle="Successfully delivered"
          color="emerald"
          icon={
            <span>
              ✅
            </span>
          }
        />


        <StatsCard
          title="Failed Emails"
          value={stats.failed_emails}
          subtitle="Delivery errors"
          color="rose"
          icon={
            <span>
              ⚠️
            </span>
          }
        />


        <StatsCard
          title="Open Rate"
          value={`${stats.open_rate}%`}
          subtitle="Tracking coming soon"
          color="amber"
          icon={
            <span>
              👁️
            </span>
          }
        />


      </div>



      {/* ACTIVITY TABLE */}


      <div className="rounded-xl border border-slate-200 bg-white shadow-sm">


        <div className="border-b border-slate-200 px-6 py-4">

          <h2 className="text-lg font-semibold text-slate-900">
            Recent Activity
          </h2>

          <p className="text-sm text-slate-500">
            Latest email send attempts
          </p>

        </div>


        {
          logs.length === 0 ? (

            <div className="px-6 py-12 text-center text-sm text-slate-400">

              No email activity yet. Create and send a campaign to get started.

            </div>

          ) : (

            <table className="w-full text-left text-sm">


              <thead>

                <tr className="border-b bg-slate-50">

                  <th className="px-6 py-3">
                    Recipient
                  </th>

                  <th className="px-6 py-3">
                    Email
                  </th>

                  <th className="px-6 py-3">
                    Status
                  </th>

                  <th className="px-6 py-3">
                    Date
                  </th>

                </tr>

              </thead>


              <tbody>


                {logs.map((log, index) => (

                  <tr 
                    key={log._id || index}
                    className="border-b"
                  >

                    <td className="px-6 py-3">
                      {log.name || "-"}
                    </td>


                    <td className="px-6 py-3">
                      {log.email || "-"}
                    </td>


                    <td className="px-6 py-3">
                      {log.status || "-"}
                    </td>


                    <td className="px-6 py-3">

                      {
                        log.sent_at
                        ? new Date(log.sent_at).toLocaleString()
                        : "-"
                      }

                    </td>


                  </tr>

                ))}


              </tbody>


            </table>

          )
        }


      </div>


    </div>
  )
}
import { useCallback, useEffect, useState } from 'react'
import { getCampaignTemplates, launchCampaign, previewCampaign } from '../api/axios'

const CUSTOM_TEMPLATE = 'custom'

const DEFAULT_CUSTOM_HTML = `<p>Hi {{ name }},</p>
<p>You are invited to join <strong>SynkSpace</strong>.</p>
<p>As a <strong>{{ category }}</strong> creator in {{ city }}, we'd love to collaborate with you on {{ platform }} ({{ handle }}).</p>
<p>Best,<br/>The SynkSpace Team</p>`

const TEMPLATE_LABELS = {
  founding_creator: 'Founding Creator Invite',
  follow_up: 'Creator Follow Up',
  brand_invite: 'Brand Invite',
  event_invite: 'Event Organizer Invite',
  custom: 'Custom HTML Template',
}

export default function CampaignForm({ onSuccess }) {
  const [name, setName] = useState('')
  const [subject, setSubject] = useState("You're invited to join SynkSpace")
  const [templateType, setTemplateType] = useState('founding_creator')
  const [htmlTemplate, setHtmlTemplate] = useState(DEFAULT_CUSTOM_HTML)
  const [categoryFilter, setCategoryFilter] = useState('')
  const [csvFile, setCsvFile] = useState(null)
  const [dragging, setDragging] = useState(false)

  const [loading, setLoading] = useState(false)
  const [previewing, setPreviewing] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [preview, setPreview] = useState(null)

  useEffect(() => {
    getCampaignTemplates().catch(() => {
      // Fallback if templates endpoint unavailable
    })
  }, [])

  const handleCsvFile = useCallback((selected) => {
    if (!selected) return
    if (!selected.name.toLowerCase().endsWith('.csv')) {
      setError('Please select a .csv file')
      return
    }
    setCsvFile(selected)
    setError(null)
    setPreview(null)
  }, [])

  const validateForm = () => {
    if (!name.trim()) return 'Campaign name is required.'
    if (!subject.trim()) return 'Email subject is required.'
    if (!csvFile) return 'Please upload a CSV file.'
    if (templateType === CUSTOM_TEMPLATE && !htmlTemplate.trim()) {
      return 'Custom template HTML is required.'
    }
    return null
  }

  const handlePreview = async () => {
    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      return
    }

    try {
      setPreviewing(true)
      setError(null)
      const res = await previewCampaign(
        csvFile,
        templateType,
        templateType === CUSTOM_TEMPLATE ? htmlTemplate : ''
      )
      setPreview(res.data)
    } catch (err) {
      setError(err.message)
      setPreview(null)
    } finally {
      setPreviewing(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      return
    }

    try {
      setLoading(true)
      setError(null)
      setSuccess(null)

      await launchCampaign({
        file: csvFile,
        name: name.trim(),
        subject: subject.trim(),
        templateType,
        htmlTemplate: templateType === CUSTOM_TEMPLATE ? htmlTemplate : '',
        categoryFilter: categoryFilter.trim(),
      })

      setSuccess('Campaign launched! Emails are being sent — check the dashboard for progress.')
      setName('')
      setSubject("You're invited to join SynkSpace")
      setTemplateType('founding_creator')
      setHtmlTemplate(DEFAULT_CUSTOM_HTML)
      setCategoryFilter('')
      setCsvFile(null)
      setPreview(null)
      onSuccess?.()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const isCustom = templateType === CUSTOM_TEMPLATE

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-slate-700">Campaign Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Q1 Lifestyle Outreach"
          className="mt-1.5 w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">Email Subject</label>
        <input
          type="text"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          className="mt-1.5 w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">Template</label>
        <select
          value={templateType}
          onChange={(e) => {
            setTemplateType(e.target.value)
            setPreview(null)
          }}
          className="mt-1.5 w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
        >
          <option value="founding_creator">{TEMPLATE_LABELS.founding_creator}</option>
          <option value="follow_up">{TEMPLATE_LABELS.follow_up}</option>
          <option value="brand_invite">{TEMPLATE_LABELS.brand_invite}</option>
          <option value="event_invite">{TEMPLATE_LABELS.event_invite}</option>
          <option value="custom">{TEMPLATE_LABELS.custom}</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">Recipient CSV</label>
        <div
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragging(false)
            handleCsvFile(e.dataTransfer.files[0])
          }}
          className={`relative mt-1.5 rounded-xl border-2 border-dashed p-6 text-center transition-colors ${
            dragging
              ? 'border-brand-400 bg-brand-50'
              : csvFile
                ? 'border-emerald-300 bg-emerald-50'
                : 'border-slate-300 bg-slate-50 hover:border-brand-300'
          }`}
        >
          {csvFile ? (
            <div>
              <p className="text-sm font-medium text-slate-900">{csvFile.name}</p>
              <p className="mt-1 text-xs text-slate-500">{(csvFile.size / 1024).toFixed(1)} KB</p>
            </div>
          ) : (
            <div>
              <p className="text-sm font-medium text-slate-600">Drag & drop CSV here</p>
              <p className="mt-1 text-xs text-slate-400">Required: name, email · Optional: category, city, handle, platform</p>
            </div>
          )}
          <input
            type="file"
            accept=".csv"
            className="absolute inset-0 cursor-pointer opacity-0"
            onChange={(e) => handleCsvFile(e.target.files[0])}
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-700">
          Category Filter <span className="font-normal text-slate-400">(optional)</span>
        </label>
        <input
          type="text"
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          placeholder="e.g. Lifestyle — leave blank to send to all rows"
          className="mt-1.5 w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
        />
      </div>

      {isCustom && (
        <div>
          <div className="flex items-center justify-between">
            <label className="block text-sm font-medium text-slate-700">Custom HTML Template</label>
            <span className="text-xs text-slate-400">
              {'{{ name }}'}, {'{{ category }}'}, {'{{ city }}'}, {'{{ handle }}'}, {'{{ platform }}'}
            </span>
          </div>
          <textarea
            value={htmlTemplate}
            onChange={(e) => {
              setHtmlTemplate(e.target.value)
              setPreview(null)
            }}
            rows={10}
            className="mt-1.5 w-full rounded-lg border border-slate-300 px-4 py-3 font-mono text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500/20"
          />
        </div>
      )}

      {preview && (
        <div className="rounded-xl border border-slate-200 bg-white overflow-hidden">
          <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
            <p className="text-sm font-semibold text-slate-900">Email Preview</p>
            <p className="text-xs text-slate-500">
              Rendered for <strong>{preview.recipient.name}</strong> ({preview.recipient.email})
              · {preview.total_recipients} total recipients
            </p>
          </div>
          <div
            className="max-h-80 overflow-y-auto p-4"
            dangerouslySetInnerHTML={{ __html: preview.preview_html }}
          />
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      )}

      {success && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {success}
        </div>
      )}

      <div className="flex gap-3">
        <button
          type="button"
          onClick={handlePreview}
          disabled={previewing || loading}
          className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm transition-colors hover:bg-slate-50 disabled:opacity-50"
        >
          {previewing ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
              Generating Preview...
            </>
          ) : (
            <>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Preview Email
            </>
          )}
        </button>

        <button
          type="submit"
          disabled={loading || previewing}
          className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-brand-600 to-violet-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition-all hover:shadow-md disabled:opacity-50"
        >
          {loading ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Sending...
            </>
          ) : (
            <>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              Send Campaign
            </>
          )}
        </button>
      </div>
    </form>
  )
}

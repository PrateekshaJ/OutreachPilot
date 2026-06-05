import { useCallback, useState } from 'react'
import { uploadCreatorsCSV } from '../api/axios'

export default function UploadCSV() {
  const [dragging, setDragging] = useState(false)
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFile = useCallback((selected) => {
    if (!selected) return
    if (!selected.name.toLowerCase().endsWith('.csv')) {
      setError('Please select a .csv file')
      return
    }
    setFile(selected)
    setError(null)
    setResult(null)
  }, [])

  const onDrop = useCallback(
    (e) => {
      e.preventDefault()
      setDragging(false)
      handleFile(e.dataTransfer.files[0])
    },
    [handleFile]
  )

  const handleUpload = async () => {
    if (!file) return
    try {
      setUploading(true)
      setError(null)
      const res = await uploadCreatorsCSV(file)
      setResult(res.data)
      setFile(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Upload Creators</h1>
        <p className="mt-1 text-sm text-slate-500">
          Import influencers from a CSV file. Required columns: name, email, instagram, category.
        </p>
      </div>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`relative rounded-2xl border-2 border-dashed p-12 text-center transition-colors ${
          dragging
            ? 'border-brand-400 bg-brand-50'
            : 'border-slate-300 bg-white hover:border-brand-300'
        }`}
      >
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-brand-50">
          <svg className="h-8 w-8 text-brand-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <p className="mt-4 text-base font-medium text-slate-700">
          Drag & drop your CSV here
        </p>
        <p className="mt-1 text-sm text-slate-400">or click to browse files</p>
        <input
          type="file"
          accept=".csv"
          className="absolute inset-0 cursor-pointer opacity-0"
          onChange={(e) => handleFile(e.target.files[0])}
        />
      </div>

      {file && (
        <div className="mt-4 flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50">
              <svg className="h-5 w-5 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-slate-900">{file.name}</p>
              <p className="text-xs text-slate-400">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="rounded-lg bg-brand-600 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-brand-700 disabled:opacity-50"
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      )}

      {error && (
        <div className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3">
          <p className="text-sm font-medium text-emerald-800">{result.message}</p>
          <p className="mt-1 text-sm text-emerald-700">
            Inserted: {result.inserted} · Updated: {result.updated} · Total: {result.total_processed}
          </p>
          {result.errors?.length > 0 && (
            <ul className="mt-2 list-inside list-disc text-xs text-amber-700">
              {result.errors.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      <div className="mt-8 rounded-xl border border-slate-200 bg-white p-6">
        <h3 className="text-sm font-semibold text-slate-900">CSV Format</h3>
        <pre className="mt-3 overflow-x-auto rounded-lg bg-slate-50 p-4 text-xs text-slate-600">
{`name,email,instagram,category
Alex Rivera,alex@example.com,@alexrivera,Lifestyle
Jordan Kim,jordan@example.com,@jordankim,Fitness`}
        </pre>
      </div>
    </div>
  )
}

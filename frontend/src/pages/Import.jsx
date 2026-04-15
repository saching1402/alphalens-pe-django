import { useState, useRef } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { importExcel } from '../lib/api'

export default function Import() {
  const qc = useQueryClient()
  const [dragging, setDragging] = useState(false)
  const [result, setResult] = useState(null)
  const fileRef = useRef()

  const mut = useMutation({
    mutationFn: importExcel,
    onSuccess: (data) => {
      setResult(data)
      qc.invalidateQueries(['managers'])
      qc.invalidateQueries(['funds'])
      toast.success(`Imported: ${data.managers_created} new managers, ${data.funds_created} new funds`)
    },
    onError: (err) => toast.error(err?.response?.data?.detail || 'Import failed'),
  })

  const handleFile = (file) => {
    if (!file) return
    if (!file.name.match(/\.(xlsx|xls)$/i)) { toast.error('Please select an Excel file (.xlsx or .xls)'); return }
    mut.mutate(file)
  }

  return (
    <div>
      <div className="page-title">Import Data</div>
      <div className="page-sub">Upload your PE fund manager Excel file to populate the platform</div>

      <div className="card" style={{ maxWidth: 600, marginTop: 8 }}>
        <div
          style={{
            border: `2px dashed ${dragging ? 'var(--gold)' : 'var(--border2)'}`,
            borderRadius: 10, padding: '48px 32px', textAlign: 'center', cursor: 'pointer',
            background: dragging ? 'var(--gold-dim2)' : 'transparent', transition: 'all .2s',
          }}
          onClick={() => fileRef.current.click()}
          onDragOver={e => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={e => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]) }}
        >
          <div style={{ fontSize: 32, marginBottom: 12 }}>📊</div>
          <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 6 }}>
            {mut.isPending ? 'Importing…' : 'Drop Excel file here or click to browse'}
          </div>
          <div style={{ color: 'var(--text3)', fontSize: 13 }}>Supports .xlsx and .xls</div>
          <input ref={fileRef} type="file" accept=".xlsx,.xls" style={{ display: 'none' }} onChange={e => handleFile(e.target.files[0])} />
        </div>

        {result && (
          <div style={{ marginTop: 20, padding: '16px 20px', background: 'var(--bg3)', borderRadius: 8, border: '1px solid var(--border)' }}>
            <div style={{ fontWeight: 600, color: 'var(--green)', marginBottom: 10 }}>✓ Import Complete</div>
            {[
              ['Managers Created', result.managers_created],
              ['Managers Updated', result.managers_updated],
              ['Funds Created', result.funds_created],
              ['Funds Updated', result.funds_updated],
            ].map(([label, val]) => (
              <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--border)', fontSize: 13 }}>
                <span style={{ color: 'var(--text2)' }}>{label}</span>
                <span className="mono" style={{ color: 'var(--gold2)' }}>{val}</span>
              </div>
            ))}
            {result.errors?.length > 0 && (
              <div style={{ marginTop: 10, color: 'var(--red)', fontSize: 12 }}>
                {result.errors.length} errors — check your column names match the expected format
              </div>
            )}
          </div>
        )}
      </div>

      <div className="card" style={{ maxWidth: 600, marginTop: 20 }}>
        <div className="section-title">Expected Excel Format</div>
        <p style={{ color: 'var(--text2)', fontSize: 13, marginBottom: 12 }}>
          Your Excel file should have a fund-level sheet with columns like:
        </p>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {['Fund Manager','Fund Name','Vintage','Fund Size (USD M)','IRR (%)','TVPI','DPI','Fund Quartile','IRR Benchmark','Strategy'].map(col => (
            <span key={col} style={{ background: 'var(--bg3)', border: '1px solid var(--border)', padding: '3px 8px', borderRadius: 4, fontSize: 12, fontFamily: 'var(--mono)', color: 'var(--teal)' }}>
              {col}
            </span>
          ))}
        </div>
        <p style={{ color: 'var(--text3)', fontSize: 12, marginTop: 12 }}>
          Optionally include a "Consol View" sheet with manager-level AUM, PB Score, and Description.
        </p>
      </div>
    </div>
  )
}

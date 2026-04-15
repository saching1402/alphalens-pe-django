import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { fetchWorkflows, fetchManagers, createWorkflow, updateWorkflow, deleteWorkflow, addComment } from '../lib/api'
import { statusBadge } from '../lib/utils'

const STATUS_OPTS = ['Open','In Progress','Due Diligence','Committed','Declined','Watchlist','Resolved','Closed']
const TYPE_OPTS = ['Due Diligence','Clarification','Risk Review','Performance','Other']
const PRIORITY_OPTS = ['High','Medium','Low']

export default function Workflows() {
  const qc = useQueryClient()
  const [selected, setSelected] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [comment, setComment] = useState('')
  const [form, setForm] = useState({ manager: '', title: '', type: 'Due Diligence', status: 'Open', priority: 'Medium', description: '' })
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const { data: workflows = [] } = useQuery({ queryKey: ['workflows'], queryFn: () => fetchWorkflows({}) })
  const { data: managers = [] } = useQuery({ queryKey: ['managers'], queryFn: () => fetchManagers({}) })

  const createMut = useMutation({
    mutationFn: createWorkflow,
    onSuccess: (wf) => { qc.invalidateQueries(['workflows']); toast.success('Workflow created'); setShowForm(false); setSelected(wf) },
  })

  const updateMut = useMutation({
    mutationFn: ({ id, data }) => updateWorkflow(id, data),
    onSuccess: (wf) => { qc.invalidateQueries(['workflows']); setSelected(wf); toast.success('Updated') },
  })

  const deleteMut = useMutation({
    mutationFn: deleteWorkflow,
    onSuccess: () => { qc.invalidateQueries(['workflows']); setSelected(null); toast.success('Deleted') },
  })

  const commentMut = useMutation({
    mutationFn: ({ id, body }) => addComment(id, { body, author: 'User' }),
    onSuccess: () => { qc.invalidateQueries(['workflows']); setComment('') },
  })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div><div className="page-title">Workflows</div><div className="page-sub">Due diligence tracking, notes, and status management</div></div>
        <button className="btn btn-gold" onClick={() => setShowForm(f => !f)}>+ New Workflow</button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="section-title" style={{ marginBottom: 16 }}>New Workflow</div>
          <div className="form-grid">
            <div className="form-group">
              <label>Manager *</label>
              <select value={form.manager} onChange={e => set('manager', e.target.value)}>
                <option value="">Select</option>
                {managers.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
              </select>
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Title *</label>
              <input value={form.title} onChange={e => set('title', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Type</label>
              <select value={form.type} onChange={e => set('type', e.target.value)}>
                {TYPE_OPTS.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Status</label>
              <select value={form.status} onChange={e => set('status', e.target.value)}>
                {STATUS_OPTS.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Priority</label>
              <select value={form.priority} onChange={e => set('priority', e.target.value)}>
                {PRIORITY_OPTS.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            </div>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label>Description</label>
              <textarea rows={3} value={form.description} onChange={e => set('description', e.target.value)} />
            </div>
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
            <button className="btn btn-gold" onClick={() => createMut.mutate(form)} disabled={!form.title || !form.manager}>
              {createMut.isPending ? 'Creating…' : 'Create Workflow'}
            </button>
            <button className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: selected ? '360px 1fr' : '1fr', gap: 20 }}>
        <div className="card" style={{ padding: 0 }}>
          <div className="tbl-wrap">
            <table>
              <thead><tr><th>Title</th><th>Manager</th><th>Type</th><th>Status</th><th>Priority</th></tr></thead>
              <tbody>
                {workflows.map(wf => (
                  <tr key={wf.id} onClick={() => setSelected(wf)} style={{ cursor: 'pointer', background: selected?.id === wf.id ? 'var(--gold-dim2)' : '' }}>
                    <td style={{ fontWeight: 500 }}>{wf.title}</td>
                    <td style={{ color: 'var(--text2)' }}>{wf.manager_name}</td>
                    <td style={{ color: 'var(--text3)' }}>{wf.type}</td>
                    <td><span className={statusBadge(wf.status)}>{wf.status}</span></td>
                    <td style={{ color: wf.priority === 'High' ? 'var(--red)' : wf.priority === 'Low' ? 'var(--text3)' : 'var(--amber)' }}>{wf.priority}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {selected && (
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <div style={{ fontSize: 17, fontWeight: 700 }}>{selected.title}</div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button className="btn btn-danger btn-sm" onClick={() => { if(confirm('Delete?')) deleteMut.mutate(selected.id) }}>Delete</button>
                <button className="btn btn-ghost btn-sm" onClick={() => setSelected(null)}>✕</button>
              </div>
            </div>

            <div style={{ display: 'flex', gap: 10, marginBottom: 16, flexWrap: 'wrap' }}>
              <select value={selected.status} onChange={e => updateMut.mutate({ id: selected.id, data: { status: e.target.value } })} style={{ width: 160 }}>
                {STATUS_OPTS.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
              <select value={selected.priority} onChange={e => updateMut.mutate({ id: selected.id, data: { priority: e.target.value } })} style={{ width: 120 }}>
                {PRIORITY_OPTS.map(o => <option key={o} value={o}>{o}</option>)}
              </select>
            </div>

            {selected.description && <p style={{ color: 'var(--text2)', marginBottom: 20, fontSize: 13 }}>{selected.description}</p>}

            <div className="section-title">Comments ({selected.comments?.length || 0})</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 16, maxHeight: 300, overflowY: 'auto' }}>
              {(selected.comments || []).map(c => (
                <div key={c.id} style={{ background: 'var(--bg3)', borderRadius: 8, padding: '10px 14px', border: '1px solid var(--border)' }}>
                  <div style={{ fontSize: 12, color: 'var(--text3)', marginBottom: 4 }}>{c.author} · {new Date(c.created_at).toLocaleDateString()}</div>
                  <div style={{ color: 'var(--text)', fontSize: 13 }}>{c.body}</div>
                </div>
              ))}
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <input value={comment} onChange={e => setComment(e.target.value)} placeholder="Add a comment…" onKeyDown={e => e.key === 'Enter' && comment && commentMut.mutate({ id: selected.id, body: comment })} />
              <button className="btn btn-gold btn-sm" onClick={() => comment && commentMut.mutate({ id: selected.id, body: comment })} disabled={!comment}>Post</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

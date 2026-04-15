import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { fetchManagers, createManager, updateManager, deleteManager } from '../lib/api'
import { fmt1, fmt2, fmtM, irrClass, tvpiClass, strategyBadge, alphaClass, statusBadge } from '../lib/utils'

function ManagerModal({ manager, onClose }) {
  const qc = useQueryClient()
  const isEdit = !!manager?.id
  const [form, setForm] = useState({
    name: manager?.name || '',
    strategy: manager?.strategy || '',
    pb_score: manager?.pb_score ?? '',
    aum_usd_m: manager?.aum_usd_m ?? '',
    description: manager?.description || '',
    year_founded: manager?.year_founded ?? '',
    segment: manager?.segment || '',
    latest_fund_size_usd_m: manager?.latest_fund_size_usd_m ?? '',
  })
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const mut = useMutation({
    mutationFn: (d) => isEdit ? updateManager(manager.id, d) : createManager(d),
    onSuccess: () => { qc.invalidateQueries(['managers']); toast.success(isEdit ? 'Manager updated' : 'Manager created'); onClose() },
    onError: () => toast.error('Save failed'),
  })

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h2>{isEdit ? 'Edit Fund Manager' : 'Add Fund Manager'}</h2>
          <button className="btn btn-ghost btn-sm" onClick={onClose}>✕</button>
        </div>
        <div className="form-grid">
          {[['name','Name *'],['strategy','Strategy (MM/LMM)'],['pb_score','PB Score'],['aum_usd_m','AUM (USD M)'],
            ['year_founded','Year Founded'],['segment','Segment'],['latest_fund_size_usd_m','Latest Fund Size (USD M)']].map(([k, label]) => (
            <div className="form-group" key={k}>
              <label>{label}</label>
              {k === 'strategy' ? (
                <select value={form[k]} onChange={e => set(k, e.target.value)}>
                  <option value="">Select</option>
                  <option value="MM">Mid-Market (MM)</option>
                  <option value="LMM">Lower Mid-Market (LMM)</option>
                </select>
              ) : (
                <input value={form[k]} onChange={e => set(k, e.target.value)} placeholder={label} />
              )}
            </div>
          ))}
          <div className="form-group" style={{ gridColumn: '1 / -1' }}>
            <label>Description</label>
            <textarea rows={3} value={form.description} onChange={e => set('description', e.target.value)} />
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-gold" onClick={() => mut.mutate(form)} disabled={!form.name}>
            {mut.isPending ? 'Saving…' : isEdit ? 'Save Changes' : 'Create Manager'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Managers() {
  const qc = useQueryClient()
  const [search, setSearch] = useState('')
  const [strategy, setStrategy] = useState('')
  const [modal, setModal] = useState(null)
  const [selected, setSelected] = useState(null)

  const { data: managers = [], isLoading } = useQuery({ queryKey: ['managers', search, strategy], queryFn: () => fetchManagers({ search, strategy }) })

  const delMut = useMutation({
    mutationFn: deleteManager,
    onSuccess: () => { qc.invalidateQueries(['managers']); toast.success('Deleted'); setSelected(null) },
    onError: () => toast.error('Delete failed'),
  })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div><div className="page-title">Fund Managers</div><div className="page-sub">Full manager roster with computed metrics</div></div>
        <button className="btn btn-gold" onClick={() => setModal('create')}>+ Add Manager</button>
      </div>

      <div className="filter-bar">
        <input placeholder="Search managers…" value={search} onChange={e => setSearch(e.target.value)} style={{ width: 220 }} />
        <select value={strategy} onChange={e => setStrategy(e.target.value)} style={{ width: 160 }}>
          <option value="">All Strategies</option>
          <option value="MM">Mid-Market</option>
          <option value="LMM">Lower Mid-Market</option>
        </select>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: selected ? '340px 1fr' : '1fr', gap: 20 }}>
        <div className="card" style={{ padding: 0 }}>
          <div className="tbl-wrap">
            <table>
              <thead>
                <tr>
                  <th>Manager</th><th>Strategy</th><th>Avg IRR</th><th>Avg TVPI</th><th>Funds</th><th>Status</th><th></th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr><td colSpan={7} style={{ textAlign: 'center', color: 'var(--text3)', padding: 32 }}>Loading…</td></tr>
                ) : managers.map(m => (
                  <tr key={m.id} onClick={() => setSelected(m)} style={{ cursor: 'pointer', background: selected?.id === m.id ? 'var(--gold-dim2)' : '' }}>
                    <td style={{ fontWeight: 600 }}>
                      {m.name}
                      {m.workflow_status && <span style={{ marginLeft: 6 }}><span className={statusBadge(m.workflow_status)}>{m.workflow_status}</span></span>}
                    </td>
                    <td>{m.strategy && <span className={strategyBadge(m.strategy)}>{m.strategy}</span>}</td>
                    <td className={irrClass(m.avg_irr)}>{fmt1(m.avg_irr)}</td>
                    <td className={tvpiClass(m.avg_tvpi)}>{fmt2(m.avg_tvpi)}</td>
                    <td className="mono">{m.fund_count}</td>
                    <td></td>
                    <td onClick={e => e.stopPropagation()}>
                      <button className="btn btn-ghost btn-sm" onClick={() => setModal(m)} style={{ marginRight: 4 }}>Edit</button>
                      <button className="btn btn-danger btn-sm" onClick={() => { if(confirm('Delete?')) delMut.mutate(m.id) }}>Del</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {selected && (
          <div className="card" style={{ overflowY: 'auto', maxHeight: 'calc(100vh - 160px)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <div style={{ fontSize: 17, fontWeight: 700 }}>{selected.name}</div>
              <button className="btn btn-ghost btn-sm" onClick={() => setSelected(null)}>✕</button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 20 }}>
              {[
                ['Avg IRR', fmt1(selected.avg_irr), irrClass(selected.avg_irr)],
                ['Avg TVPI', fmt2(selected.avg_tvpi), tvpiClass(selected.avg_tvpi)],
                ['Avg DPI', fmt2(selected.avg_dpi)],
                ['Alpha vs Bench', selected.alpha_vs_benchmark != null ? (selected.alpha_vs_benchmark > 0 ? '+' : '') + fmt1(selected.alpha_vs_benchmark) : '—', alphaClass(selected.alpha_vs_benchmark)],
                ['AUM', fmtM(selected.aum_usd_m)],
                ['Top Quartile Funds', selected.top_quartile_count ?? '—'],
                ['PB Score', selected.pb_score ?? '—'],
                ['Fund Count', selected.fund_count],
              ].map(([label, val, cls]) => (
                <div className="stat-card" key={label} style={{ padding: '12px 14px' }}>
                  <div className="label">{label}</div>
                  <div className="value" style={{ fontSize: 18 }}><span className={cls}>{val}</span></div>
                </div>
              ))}
            </div>
            {selected.description && <p style={{ color: 'var(--text2)', fontSize: 13, marginBottom: 20 }}>{selected.description}</p>}
            <div className="section-title">Funds ({selected.funds?.length})</div>
            <div className="tbl-wrap">
              <table>
                <thead><tr><th>Fund</th><th>Vintage</th><th>IRR</th><th>TVPI</th><th>DPI</th><th>Quartile</th></tr></thead>
                <tbody>
                  {(selected.funds || []).map(f => (
                    <tr key={f.id}>
                      <td style={{ fontWeight: 500 }}>{f.fund_name}</td>
                      <td className="mono">{f.vintage || '—'}</td>
                      <td className={irrClass(f.irr)}>{fmt1(f.irr)}</td>
                      <td className={tvpiClass(f.tvpi)}>{fmt2(f.tvpi)}</td>
                      <td className="mono">{fmt2(f.dpi)}</td>
                      <td>{f.fund_quartile ? f.fund_quartile.substring(0, 1) : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {modal && <ManagerModal manager={modal === 'create' ? null : modal} onClose={() => setModal(null)} />}
    </div>
  )
}

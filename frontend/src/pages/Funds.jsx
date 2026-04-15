import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { fetchFunds, fetchManagers, createFund, updateFund, deleteFund } from '../lib/api'
import { fmt1, fmt2, irrClass, tvpiClass } from '../lib/utils'

const QUARTILE_OPTIONS = ['', '1 (Top Quartile)', '2 (Upper-Mid Quartile)', '3 (Lower-Mid Quartile)', '4 (Bottom Quartile)']

function FundModal({ fund, managers, onClose }) {
  const qc = useQueryClient()
  const isEdit = !!fund?.id
  const [form, setForm] = useState({
    manager_id: fund?.manager_id || '',
    fund_name: fund?.fund_name || '',
    fund_id_raw: fund?.fund_id_raw || '',
    vintage: fund?.vintage ?? '',
    fund_size_usd_m: fund?.fund_size_usd_m ?? '',
    fund_type: fund?.fund_type || 'Buyout',
    investments: fund?.investments ?? '',
    irr: fund?.irr ?? '',
    tvpi: fund?.tvpi ?? '',
    rvpi: fund?.rvpi ?? '',
    dpi: fund?.dpi ?? '',
    moic: fund?.moic ?? '',
    fund_quartile: fund?.fund_quartile || '',
    irr_benchmark: fund?.irr_benchmark ?? '',
    tvpi_benchmark: fund?.tvpi_benchmark ?? '',
    dpi_benchmark: fund?.dpi_benchmark ?? '',
    as_of_quarter: fund?.as_of_quarter || '',
    as_of_year: fund?.as_of_year ?? '',
    geography: fund?.geography || '',
    sector_focus: fund?.sector_focus || '',
  })
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const mut = useMutation({
    mutationFn: d => isEdit ? updateFund(fund.id, d) : createFund(d),
    onSuccess: () => { qc.invalidateQueries(['funds']); qc.invalidateQueries(['managers']); toast.success(isEdit ? 'Fund updated' : 'Fund created'); onClose() },
    onError: () => toast.error('Save failed'),
  })

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h2>{isEdit ? 'Edit Fund' : 'Add Fund'}</h2>
          <button className="btn btn-ghost btn-sm" onClick={onClose}>✕</button>
        </div>
        <div className="form-grid">
          <div className="form-group" style={{ gridColumn: '1 / -1' }}>
            <label>Fund Manager *</label>
            <select value={form.manager_id} onChange={e => set('manager_id', e.target.value)}>
              <option value="">Select manager</option>
              {managers.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
            </select>
          </div>
          {[['fund_name','Fund Name *'],['fund_id_raw','Preqin / Raw ID'],['vintage','Vintage Year'],['fund_size_usd_m','Fund Size (USD M)'],
            ['investments','# Investments'],['irr','IRR (%)'],['tvpi','TVPI'],['dpi','DPI'],['rvpi','RVPI'],['moic','MOIC'],
            ['irr_benchmark','IRR Benchmark (%)'],['tvpi_benchmark','TVPI Benchmark'],['dpi_benchmark','DPI Benchmark'],
            ['as_of_quarter','As Of Quarter'],['as_of_year','As Of Year'],['geography','Geography'],['sector_focus','Sector Focus']].map(([k, label]) => (
            <div className="form-group" key={k}>
              <label>{label}</label>
              <input value={form[k]} onChange={e => set(k, e.target.value)} placeholder={label} />
            </div>
          ))}
          <div className="form-group">
            <label>Fund Type</label>
            <select value={form.fund_type} onChange={e => set('fund_type', e.target.value)}>
              {['Buyout','Growth','Venture','Debt','Real Assets','Other'].map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Quartile</label>
            <select value={form.fund_quartile} onChange={e => set('fund_quartile', e.target.value)}>
              {QUARTILE_OPTIONS.map(q => <option key={q} value={q}>{q || 'N/A'}</option>)}
            </select>
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-gold" onClick={() => mut.mutate(form)} disabled={!form.fund_name || !form.manager_id}>
            {mut.isPending ? 'Saving…' : isEdit ? 'Save Changes' : 'Create Fund'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Funds() {
  const qc = useQueryClient()
  const [modal, setModal] = useState(null)
  const [managerFilter, setManagerFilter] = useState('')

  const { data: funds = [], isLoading } = useQuery({ queryKey: ['funds', managerFilter], queryFn: () => fetchFunds(managerFilter ? { manager_id: managerFilter } : {}) })
  const { data: managers = [] } = useQuery({ queryKey: ['managers'], queryFn: () => fetchManagers({}) })

  const delMut = useMutation({
    mutationFn: deleteFund,
    onSuccess: () => { qc.invalidateQueries(['funds']); qc.invalidateQueries(['managers']); toast.success('Fund deleted') },
  })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div><div className="page-title">Funds</div><div className="page-sub">Individual fund performance records</div></div>
        <button className="btn btn-gold" onClick={() => setModal('create')}>+ Add Fund</button>
      </div>
      <div className="filter-bar">
        <select value={managerFilter} onChange={e => setManagerFilter(e.target.value)} style={{ width: 240 }}>
          <option value="">All Managers</option>
          {managers.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
        </select>
      </div>
      <div className="card" style={{ padding: 0 }}>
        <div className="tbl-wrap">
          <table>
            <thead>
              <tr><th>Fund</th><th>Manager</th><th>Vintage</th><th>Size</th><th>IRR</th><th>TVPI</th><th>DPI</th><th>Quartile</th><th></th></tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={9} style={{ textAlign: 'center', color: 'var(--text3)', padding: 32 }}>Loading…</td></tr>
              ) : funds.map(f => (
                <tr key={f.id}>
                  <td style={{ fontWeight: 500 }}>{f.fund_name}</td>
                  <td style={{ color: 'var(--text2)' }}>{f.manager_name}</td>
                  <td className="mono">{f.vintage || '—'}</td>
                  <td className="mono">{f.fund_size_usd_m ? `$${Number(f.fund_size_usd_m).toFixed(0)}M` : '—'}</td>
                  <td className={irrClass(f.irr)}>{fmt1(f.irr)}</td>
                  <td className={tvpiClass(f.tvpi)}>{fmt2(f.tvpi)}</td>
                  <td className="mono">{fmt2(f.dpi)}</td>
                  <td>{f.fund_quartile ? f.fund_quartile.substring(0, 1) : '—'}</td>
                  <td>
                    <button className="btn btn-ghost btn-sm" onClick={() => setModal(f)} style={{ marginRight: 4 }}>Edit</button>
                    <button className="btn btn-danger btn-sm" onClick={() => { if(confirm('Delete fund?')) delMut.mutate(f.id) }}>Del</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {modal && <FundModal fund={modal === 'create' ? null : modal} managers={managers} onClose={() => setModal(null)} />}
    </div>
  )
}

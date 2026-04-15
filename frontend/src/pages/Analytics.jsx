import { useState, useRef, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Scatter, Bar } from 'react-chartjs-2'
import { Chart, registerables } from 'chart.js'
import { fetchScatter, fetchTopManagers, fetchQuartileDist } from '../lib/api'
import { CHART_DEFAULTS, RANK_COLORS } from '../lib/utils'
Chart.register(...registerables)

const METRIC_OPTS = [
  { value: 'irr', label: 'Avg IRR (%)' },
  { value: 'tvpi', label: 'Avg TVPI (x)' },
  { value: 'dpi', label: 'Avg DPI (x)' },
  { value: 'aum_usd_m', label: 'AUM (USD M)' },
]

export default function Analytics() {
  const [xAxis, setXAxis] = useState('irr')
  const [yAxis, setYAxis] = useState('tvpi')
  const [metric, setMetric] = useState('irr')
  const [topN, setTopN] = useState(10)
  const [strategy, setStrategy] = useState('')
  const [showLabels, setShowLabels] = useState(true)
  const [filtersOpen, setFiltersOpen] = useState(true)

  const { data: scatter } = useQuery({ queryKey: ['scatter', xAxis, yAxis, strategy], queryFn: () => fetchScatter(xAxis, yAxis, strategy) })
  const { data: top } = useQuery({ queryKey: ['top', metric, topN, strategy], queryFn: () => fetchTopManagers(metric, topN, strategy) })
  const { data: qDist } = useQuery({ queryKey: ['quartile-dist', strategy], queryFn: () => fetchQuartileDist(strategy) })

  const scatterData = scatter ? {
    datasets: [{
      label: 'Managers',
      data: scatter.map(p => ({ x: p.x, y: p.y, name: p.name })),
      backgroundColor: scatter.map((_, i) => i < topN && showLabels ? RANK_COLORS[i % RANK_COLORS.length] : 'rgba(79,156,249,0.5)'),
      pointRadius: 6,
    }],
  } : null

  const scatterOpts = {
    ...CHART_DEFAULTS,
    plugins: {
      ...CHART_DEFAULTS.plugins,
      tooltip: {
        ...CHART_DEFAULTS.plugins.tooltip,
        callbacks: {
          label: ctx => {
            const pt = scatter?.[ctx.dataIndex]
            return pt ? `${pt.name}: (${pt.x}, ${pt.y})` : ''
          }
        }
      }
    }
  }

  const topChart = top ? {
    labels: top.map(m => m.name),
    datasets: [{ label: METRIC_OPTS.find(o => o.value === metric)?.label, data: top.map(m => m.value), backgroundColor: RANK_COLORS, borderRadius: 4 }],
  } : null

  const qChart = qDist ? {
    labels: ['Q1', 'Q2', 'Q3', 'Q4', 'N/A'],
    datasets: [{ data: [qDist['1']||0, qDist['2']||0, qDist['3']||0, qDist['4']||0, qDist['N/A']||0], backgroundColor: ['#22c55e','#c9a84c','#f59e0b','#f43f5e','#4b5e7a'], borderRadius: 4 }],
  } : null

  return (
    <div>
      <div className="page-title">Analytics</div>
      <div className="page-sub">Cross-manager performance analysis</div>

      <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 18, flexWrap: 'wrap' }}>
        <button className="collapse-btn" onClick={() => setFiltersOpen(f => !f)}>
          {filtersOpen ? '▲' : '▼'} Filters
        </button>
        {filtersOpen && <>
          <select value={strategy} onChange={e => setStrategy(e.target.value)} style={{ width: 160 }}>
            <option value="">All Strategies</option>
            <option value="MM">Mid-Market</option>
            <option value="LMM">Lower Mid-Market</option>
          </select>
          <select value={xAxis} onChange={e => setXAxis(e.target.value)} style={{ width: 160 }}>
            {METRIC_OPTS.map(o => <option key={o.value} value={o.value}>X: {o.label}</option>)}
          </select>
          <select value={yAxis} onChange={e => setYAxis(e.target.value)} style={{ width: 160 }}>
            {METRIC_OPTS.map(o => <option key={o.value} value={o.value}>Y: {o.label}</option>)}
          </select>
          <select value={metric} onChange={e => setMetric(e.target.value)} style={{ width: 160 }}>
            {METRIC_OPTS.map(o => <option key={o.value} value={o.value}>Bar: {o.label}</option>)}
          </select>
          <select value={topN} onChange={e => setTopN(Number(e.target.value))} style={{ width: 100 }}>
            {[5,10,15,20].map(n => <option key={n} value={n}>Top {n}</option>)}
          </select>
          <label style={{ display: 'flex', gap: 6, alignItems: 'center', color: 'var(--text2)', cursor: 'pointer' }}>
            <input type="checkbox" checked={showLabels} onChange={e => setShowLabels(e.target.checked)} />
            Show top labels
          </label>
        </>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div className="card">
          <div className="section-title">Scatter — {METRIC_OPTS.find(o=>o.value===xAxis)?.label} vs {METRIC_OPTS.find(o=>o.value===yAxis)?.label}</div>
          <div className="chart-wrap-lg">
            {scatterData && <Scatter data={scatterData} options={scatterOpts} />}
          </div>
        </div>
        <div className="card">
          <div className="section-title">Top {topN} by {METRIC_OPTS.find(o=>o.value===metric)?.label}</div>
          <div className="chart-wrap-lg">
            {topChart && <Bar data={topChart} options={{ ...CHART_DEFAULTS, indexAxis: 'y', plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } } }} />}
          </div>
        </div>
        <div className="card">
          <div className="section-title">Quartile Distribution</div>
          <div className="chart-wrap">
            {qChart && <Bar data={qChart} options={{ ...CHART_DEFAULTS, plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } } }} />}
          </div>
        </div>
      </div>
    </div>
  )
}

import { useQuery } from '@tanstack/react-query'
import { Bar, Doughnut } from 'react-chartjs-2'
import { Chart, registerables } from 'chart.js'
import { fetchDashboard, fetchTopManagers, fetchQuartileDist } from '../lib/api'
import { fmt1, fmt2, fmtM, CHART_DEFAULTS, RANK_COLORS } from '../lib/utils'
Chart.register(...registerables)

function StatCard({ label, value, sub }) {
  return (
    <div className="stat-card">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {sub && <div className="sub">{sub}</div>}
    </div>
  )
}

export default function Overview() {
  const { data: dash } = useQuery({ queryKey: ['dashboard'], queryFn: fetchDashboard })
  const { data: top } = useQuery({ queryKey: ['top-managers', 'irr', 10], queryFn: () => fetchTopManagers('irr', 10) })
  const { data: qDist } = useQuery({ queryKey: ['quartile-dist'], queryFn: fetchQuartileDist })

  const topChart = top ? {
    labels: top.map(m => m.name.replace(/^[A-Z]+\s\d+/, m => m)),
    datasets: [{
      label: 'Avg IRR (%)',
      data: top.map(m => m.value),
      backgroundColor: RANK_COLORS,
      borderRadius: 4,
    }],
  } : null

  const qChart = qDist ? {
    labels: ['Q1 Top', 'Q2 Upper', 'Q3 Lower', 'Q4 Bottom', 'N/A'],
    datasets: [{
      data: [qDist['1'] || 0, qDist['2'] || 0, qDist['3'] || 0, qDist['4'] || 0, qDist['N/A'] || 0],
      backgroundColor: ['#22c55e','#c9a84c','#f59e0b','#f43f5e','#4b5e7a'],
      borderWidth: 0,
    }],
  } : null

  return (
    <div>
      <div className="page-title">Portfolio Overview</div>
      <div className="page-sub">Universe summary across all tracked fund managers</div>

      <div className="card-grid" style={{ gridTemplateColumns: 'repeat(auto-fill,minmax(170px,1fr))', marginBottom: 28 }}>
        <StatCard label="Fund Managers" value={dash?.manager_count ?? '—'} />
        <StatCard label="Total Funds" value={dash?.fund_count ?? '—'} />
        <StatCard label="Total AUM" value={dash ? fmtM(dash.total_aum_usd_m) : '—'} />
        <StatCard label="Universe Avg IRR" value={dash ? fmt1(dash.universe_avg_irr) : '—'} />
        <StatCard label="Universe Avg TVPI" value={dash ? fmt2(dash.universe_avg_tvpi) : '—'} />
        <StatCard label="Universe Avg DPI" value={dash ? fmt2(dash.universe_avg_dpi) : '—'} />
        <StatCard label="Top Quartile Funds" value={dash?.top_quartile_count ?? '—'} sub={dash ? `${dash.top_quartile_pct}% of universe` : ''} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div className="card">
          <div className="section-title">Top 10 Managers by IRR</div>
          <div className="chart-wrap-lg">
            {topChart && <Bar data={topChart} options={{ ...CHART_DEFAULTS, indexAxis: 'y', plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } } }} />}
          </div>
        </div>
        <div className="card">
          <div className="section-title">Quartile Distribution</div>
          <div className="chart-wrap-lg">
            {qChart && <Doughnut data={qChart} options={{ ...CHART_DEFAULTS, cutout: '65%', scales: undefined }} />}
          </div>
        </div>
      </div>
    </div>
  )
}

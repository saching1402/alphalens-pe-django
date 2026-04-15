export const fmt1 = (v, s = '%') => v != null ? Number(v).toFixed(1) + s : '—'
export const fmt2 = (v, s = 'x') => v != null ? Number(v).toFixed(2) + s : '—'
export const fmtM = (v) => {
  if (!v) return '—'
  const n = Number(v)
  if (n >= 1000) return '$' + (n / 1000).toFixed(1) + 'B'
  return '$' + n.toFixed(0) + 'M'
}

export function irrClass(v) {
  if (v == null) return 'v-na mono'
  const n = Number(v)
  if (n >= 25) return 'v-good mono'
  if (n >= 12) return 'v-ok mono'
  return 'v-bad mono'
}
export function tvpiClass(v) {
  if (v == null) return 'v-na mono'
  const n = Number(v)
  if (n >= 2.0) return 'v-good mono'
  if (n >= 1.5) return 'v-ok mono'
  return 'v-bad mono'
}
export function alphaClass(v) {
  if (v == null) return 'v-na mono'
  const n = Number(v)
  if (n > 0) return 'v-good mono'
  if (n === 0) return 'v-ok mono'
  return 'v-bad mono'
}

export function strategyBadge(s) {
  if (s === 'MM') return 'badge badge-mm'
  if (s === 'LMM') return 'badge badge-lmm'
  return 'badge'
}

export function statusBadge(s) {
  if (!s) return 'badge'
  const sl = s.toLowerCase().replace(/\s+/g, '')
  if (sl === 'committed') return 'badge badge-committed'
  if (sl === 'duediligence') return 'badge badge-dd'
  if (sl === 'declined') return 'badge badge-declined'
  if (sl === 'watchlist') return 'badge badge-watchlist'
  return 'badge badge-open'
}

export const RANK_COLORS = [
  '#c9a84c','#e8c96e','#4f9cf9','#2dd4bf','#a78bfa',
  '#f59e0b','#22c55e','#f43f5e','#6366f1','#ec4899',
]

export const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: '#94a3b8', font: { size: 12 } } },
    tooltip: {
      backgroundColor: '#131c2d',
      borderColor: '#1e2d44',
      borderWidth: 1,
      titleColor: '#e2e8f5',
      bodyColor: '#94a3b8',
    },
  },
  scales: {
    x: { ticks: { color: '#4b5e7a' }, grid: { color: '#1e2d44' } },
    y: { ticks: { color: '#4b5e7a' }, grid: { color: '#1e2d44' } },
  },
}

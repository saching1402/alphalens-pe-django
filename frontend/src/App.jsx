import { Routes, Route, NavLink } from 'react-router-dom'
import Overview from './pages/Overview'
import Managers from './pages/Managers'
import Funds from './pages/Funds'
import Analytics from './pages/Analytics'
import Workflows from './pages/Workflows'
import Import from './pages/Import'

function Header() {
  const links = [
    { to: '/', label: 'Overview' },
    { to: '/managers', label: 'Fund Managers' },
    { to: '/funds', label: 'Funds' },
    { to: '/analytics', label: 'Analytics' },
    { to: '/workflows', label: 'Workflows' },
    { to: '/import', label: 'Import' },
  ]
  return (
    <header className="header">
      <div className="logo">⬡ AlphaLens PE</div>
      <nav className="nav">
        {links.map(l => (
          <NavLink key={l.to} to={l.to} end={l.to === '/'} className={({ isActive }) => isActive ? 'active' : ''}>
            {l.label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}

export default function App() {
  return (
    <div className="app">
      <Header />
      <main className="page">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/managers" element={<Managers />} />
          <Route path="/funds" element={<Funds />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/workflows" element={<Workflows />} />
          <Route path="/import" element={<Import />} />
        </Routes>
      </main>
    </div>
  )
}

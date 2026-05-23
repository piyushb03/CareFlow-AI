import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { Activity, LayoutDashboard, FlaskConical, Shield, Info, Plus } from 'lucide-react'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/evaluation', label: 'Evaluation', icon: FlaskConical },
  { to: '/about', label: 'About & Safety', icon: Shield },
]

export default function Layout() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top nav */}
      <header className="sticky top-0 z-50 bg-surface-950/90 backdrop-blur border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <NavLink to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-xl bg-clinical-600 flex items-center justify-center">
              <Activity size={16} className="text-white" />
            </div>
            <div>
              <span className="text-white font-semibold text-sm">CareFlow AI</span>
              <span className="text-gray-500 text-xs block leading-none">Intake & Triage Assistant</span>
            </div>
          </NavLink>

          <nav className="hidden md:flex items-center gap-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3 py-2 rounded-xl text-sm transition-all duration-150 ${
                    isActive
                      ? 'bg-clinical-600/20 text-clinical-400'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                  }`
                }
              >
                <Icon size={15} />
                {label}
              </NavLink>
            ))}
          </nav>

          <button
            onClick={() => navigate('/intake/new')}
            className="btn-primary flex items-center gap-2 text-sm"
          >
            <Plus size={15} />
            New Intake
          </button>
        </div>

        {/* Disclaimer bar */}
        <div className="bg-amber-500/8 border-t border-amber-500/10 py-1.5 px-4 text-center">
          <p className="text-amber-400/70 text-xs">
            AI-assisted intake preparation only · Not a diagnostic system · All decisions require qualified professional review
          </p>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>

      <footer className="border-t border-white/5 py-4 text-center text-gray-600 text-xs">
        CareFlow AI — Hackathon Demo · Synthetic data only · Not for clinical use
      </footer>
    </div>
  )
}

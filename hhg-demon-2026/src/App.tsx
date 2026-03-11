import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Home, Package, AlertTriangle, Database, GitBranch } from 'lucide-react'
import Overview from './pages/Overview'
import BuyWindow from './pages/BuyWindow'
import RiskCoPilot from './pages/RiskCoPilot'
import DataStory from './pages/DataStory'
import Architecture from './pages/Architecture'

function Navigation() {
  const location = useLocation()

  const navItems = [
    { path: '/', icon: Home, label: 'Overview' },
    { path: '/buy-window', icon: Package, label: 'Smart Buy Window' },
    { path: '/risk-copilot', icon: AlertTriangle, label: 'Order Execution & Risk' },
    { path: '/data-story', icon: Database, label: 'Data Story' },
    { path: '/architecture', icon: GitBranch, label: 'Architecture' },
  ]

  return (
    <nav className="flex space-x-8" aria-label="Tabs">
      {navItems.map(({ path, icon: Icon, label }) => (
        <Link
          key={path}
          to={path}
          className={`
            flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
            ${location.pathname === path
              ? 'border-hhg-primary text-hhg-primary'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }
          `}
        >
          <Icon className="w-5 h-5" />
          <span>{label}</span>
        </Link>
      ))}
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <Link to="/" className="flex items-center space-x-3 hover:opacity-80 transition-opacity">
                <div className="w-10 h-10 bg-hhg-primary rounded flex items-center justify-center">
                  <span className="text-white font-bold text-lg">HH</span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">HHG Supply Chain AI Studio</h1>
                  <p className="text-sm text-gray-500">Intelligent Workflow Co-Pilots</p>
                </div>
              </Link>
              <div className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded">
                Demo Environment
              </div>
            </div>
          </div>
        </header>

        {/* Navigation Tabs */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <Navigation />
          </div>
        </div>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/buy-window" element={<BuyWindow />} />
            <Route path="/risk-copilot" element={<RiskCoPilot />} />
            <Route path="/data-story" element={<DataStory />} />
            <Route path="/architecture" element={<Architecture />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <p className="text-center text-sm text-gray-500">
              HHG Supply Chain AI Studio • Built by First Line Software • {new Date().getFullYear()}
            </p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App

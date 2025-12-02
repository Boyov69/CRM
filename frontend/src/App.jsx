import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Home, Users, Mail, TrendingUp, Search, BarChart3, Zap } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Practices from './pages/Practices'
import Campaigns from './pages/Campaigns'
import Analytics from './pages/Analytics'
import Leads from './pages/Leads'
import Pipeline from './pages/Pipeline'
import Automation from './pages/Automation'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="sidebar">
          <div className="logo">
            <h2>🏥 CRM</h2>
          </div>
          <ul className="nav-menu">
            <li>
              <Link to="/" className="nav-link">
                <Home size={20} />
                <span>Dashboard</span>
              </Link>
            </li>
            <li>
              <Link to="/practices" className="nav-link">
                <Users size={20} />
                <span>Praktijken</span>
              </Link>
            </li>
            <li>
              <Link to="/campaigns" className="nav-link">
                <Mail size={20} />
                <span>Campagnes</span>
              </Link>
            </li>
            <li>
              <Link to="/pipeline" className="nav-link">
                <BarChart3 size={20} />
                <span>Pipeline</span>
              </Link>
            </li>
            <li>
              <Link to="/automation" className="nav-link">
                <Zap size={20} />
                <span>Automatisering</span>
              </Link>
            </li>
            <li>
              <Link to="/leads" className="nav-link">
                <Search size={20} />
                <span>Leads</span>
              </Link>
            </li>
            <li>
              <Link to="/analytics" className="nav-link">
                <TrendingUp size={20} />
                <span>Analytics</span>
              </Link>
            </li>
          </ul>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/practices" element={<Practices />} />
            <Route path="/campaigns" element={<Campaigns />} />
            <Route path="/pipeline" element={<Pipeline />} />
            <Route path="/automation" element={<Automation />} />
            <Route path="/leads" element={<Leads />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

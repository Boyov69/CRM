import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { Home, Users, Mail, TrendingUp, Search, BarChart3, Zap, MessageSquare, Inbox as InboxIcon, Menu, X } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Practices from './pages/Practices'
import Campaigns from './pages/Campaigns'
import Analytics from './pages/Analytics'
import Leads from './pages/Leads'
import Pipeline from './pages/Pipeline'
import Automation from './pages/Automation'
import Messaging from './pages/Messaging'
import Inbox from './pages/Inbox'
import './App.css'

function AppContent() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  const closeMobileMenu = () => setMobileMenuOpen(false)

  return (
    <div className="app">
      {/* Mobile Menu Toggle */}
      <button 
        className="mobile-menu-toggle"
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
      >
        {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar Overlay for Mobile */}
      <div 
        className={`sidebar-overlay ${mobileMenuOpen ? 'active' : ''}`}
        onClick={closeMobileMenu}
      />

      {/* Premium Glassmorphic Sidebar */}
      <nav className={`sidebar ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        <div className="logo">
          <h2>CRM Premium</h2>
        </div>
        <div style={{ 
          textAlign: 'center', 
          marginBottom: '1.5rem',
          paddingBottom: '1.5rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <span className="ai-indicator">AI-Powered</span>
        </div>
        <ul className="nav-menu">
          <li>
            <Link 
              to="/" 
              className={`nav-link ${isActive('/') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              <Home size={20} />
              <span>Dashboard</span>
            </Link>
          </li>
          <li>
            <Link 
              to="/practices" 
              className={`nav-link ${isActive('/practices') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              <Users size={20} />
              <span>Praktijken</span>
            </Link>
          </li>
          <li>
            <Link 
              to="/campaigns" 
              className={`nav-link ${isActive('/campaigns') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              <Mail size={20} />
              <span>Campagnes</span>
            </Link>
          </li>
          <li>
            <Link 
              to="/pipeline" 
              className={`nav-link ${isActive('/pipeline') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              <BarChart3 size={20} />
              <span>Pipeline</span>
            </Link>
          </li>
          <li>
            <Link 
              to="/automation" 
              className={`nav-link ${isActive('/automation') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              <Zap size={20} />
              <span>Automation</span>
            </Link>
          </li>
          <li>
            <Link 
              to="/leads" 
              className={`nav-link ${isActive('/leads') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              <Search size={20} />
              <span>Leads</span>
            </Link>
          </li>
          <li>
            <Link 
              to="/inbox" 
              className={`nav-link ${isActive('/inbox') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              <InboxIcon size={20} />
              <span>Inbox</span>
              <span className="badge-premium" style={{ 
                marginLeft: 'auto', 
                fontSize: '0.6875rem',
                background: 'var(--gradient-accent)',
                color: 'white',
                padding: '0.125rem 0.5rem'
              }}>NEW</span>
            </Link>
          </li>
          <li>
            <Link 
              to="/messaging" 
              className={`nav-link ${isActive('/messaging') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
              <MessageSquare size={20} />
              <span>Messaging</span>
              <span className="badge-premium" style={{ 
                marginLeft: 'auto', 
                fontSize: '0.6875rem',
                background: 'var(--gradient-accent)',
                color: 'white',
                padding: '0.125rem 0.5rem'
              }}>NEW</span>
            </Link>
          </li>
          <li>
            <Link 
              to="/analytics" 
              className={`nav-link ${isActive('/analytics') ? 'active' : ''}`}
              onClick={closeMobileMenu}
            >
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
          <Route path="/inbox" element={<Inbox />} />
          <Route path="/messaging" element={<Messaging />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App

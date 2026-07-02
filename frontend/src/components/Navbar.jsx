import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { LogOut, Home, Users, Zap, MessageSquare, FileText } from 'lucide-react'

function Navbar({ user, onLogout }) {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/dashboard" className="navbar-brand">
          <Zap size={24} style={{ display: 'inline-block', marginRight: '8px' }} />
          HVAC CRM
        </Link>
        <div className="navbar-menu">
          <Link to="/dashboard" className={isActive('/dashboard') ? 'active' : ''}>
            <Home size={18} style={{ display: 'inline-block', marginRight: '8px' }} />
            看板
          </Link>
          <Link to="/customers" className={isActive('/customers') ? 'active' : ''}>
            <Users size={18} style={{ display: 'inline-block', marginRight: '8px' }} />
            客户
          </Link>
          <Link to="/ai" className={isActive('/ai') ? 'active' : ''}>
            <Zap size={18} style={{ display: 'inline-block', marginRight: '8px' }} />
            AI 助手
          </Link>
          <Link to="/communications" className={isActive('/communications') ? 'active' : ''}>
            <MessageSquare size={18} style={{ display: 'inline-block', marginRight: '8px' }} />
            通讯
          </Link>
          <Link to="/reports" className={isActive('/reports') ? 'active' : ''}>
            <FileText size={18} style={{ display: 'inline-block', marginRight: '8px' }} />
            报表
          </Link>
        </div>
        <div className="navbar-user">
          <span className="navbar-user-name">{user?.username || '用户'}</span>
          <button className="secondary" onClick={onLogout}>
            <LogOut size={16} style={{ marginRight: '4px', display: 'inline-block' }} />
            退出
          </button>
        </div>
      </div>
    </nav>
  )
}

export default Navbar

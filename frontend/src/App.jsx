import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import axios from 'axios'
import Navbar from './components/Navbar'
import LoginPage from './pages/LoginPage'
import CustomersPage from './pages/CustomersPage'
import AIPage from './pages/AIPage'
import DashboardPage from './pages/DashboardPage'
import CommunicationsPage from './pages/CommunicationsPage'
import ReportsPage from './pages/ReportsPage'
import './App.css'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (token) {
      fetchCurrentUser()
    }
  }, [token])

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUser(response.data)
    } catch (error) {
      console.error('获取用户信息失败:', error)
      logout()
    }
  }

  const handleLogin = (newToken, userData) => {
    localStorage.setItem('token', newToken)
    setToken(newToken)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  if (!token) {
    return <LoginPage onLogin={handleLogin} />
  }

  return (
    <BrowserRouter>
      <div className="app">
        <Navbar user={user} onLogout={logout} />
        <Routes>
          <Route path="/dashboard" element={<DashboardPage token={token} />} />
          <Route path="/customers" element={<CustomersPage token={token} />} />
          <Route path="/ai" element={<AIPage token={token} />} />
          <Route path="/communications" element={<CommunicationsPage token={token} />} />
          <Route path="/reports" element={<ReportsPage token={token} />} />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App

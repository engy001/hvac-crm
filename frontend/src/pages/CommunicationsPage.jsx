import React, { useState, useEffect } from 'react'
import axios from 'axios'
import '../styles/CommunicationsPage.css'

function CommunicationsPage({ token }) {
  const [mode, setMode] = useState('send-email')
  const [customers, setCustomers] = useState([])
  const [selectedCustomers, setSelectedCustomers] = useState([])
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    fetchCustomers()
  }, [])

  const fetchCustomers = async () => {
    try {
      const response = await axios.get('/api/customers', {
        headers: { Authorization: `Bearer ${token}` },
        params: { per_page: 200 }
      })
      setCustomers(response.data.data)
    } catch (error) {
      console.error('获取客户列表失败:', error)
    }
  }

  const handleCustomerToggle = (customerId) => {
    setSelectedCustomers(prev =>
      prev.includes(customerId)
        ? prev.filter(id => id !== customerId)
        : [...prev, customerId]
    )
  }

  const handleSendEmail = async (e) => {
    e.preventDefault()
    if (!selectedCustomers.length || !message) {
      alert('请选择客户和输入消息')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post(
        '/api/communications/send-bulk-email',
        {
          customer_ids: selectedCustomers,
          message
        },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      setResult(response.data)
      setMessage('')
      setSelectedCustomers([])
    } catch (error) {
      setResult({
        error: error.response?.data?.error || '发送失败'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSendWhatsApp = async (e) => {
    e.preventDefault()
    if (!selectedCustomers.length || !message) {
      alert('请选择客户和输入消息')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post(
        '/api/communications/send-bulk-whatsapp',
        {
          customer_ids: selectedCustomers,
          message
        },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      setResult(response.data)
      setMessage('')
      setSelectedCustomers([])
    } catch (error) {
      setResult({
        error: error.response?.data?.error || '发送失败'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>📞 通讯中心</h1>
      </div>

      <div className="communications-container">
        <div className="comm-sidebar">
          <h3>选择通讯方式</h3>
          <button
            className={mode === 'send-email' ? 'active' : ''}
            onClick={() => setMode('send-email')}
          >
            📧 发送邮件
          </button>
          <button
            className={mode === 'send-whatsapp' ? 'active' : ''}
            onClick={() => setMode('send-whatsapp')}
          >
            💬 发送 WhatsApp
          </button>
        </div>

        <div className="comm-content">
          <div className="card">
            {mode === 'send-email' && (
              <>
                <h2>📧 批量发送邮件</h2>
                <form onSubmit={handleSendEmail}>
                  <div className="form-group">
                    <label>邮件内容</label>
                    <textarea
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="输入邮件内容..."
                      rows="6"
                    />
                  </div>

                  <div className="customer-selector">
                    <h3>选择收件客户 ({selectedCustomers.length})</h3>
                    <div className="customer-list">
                      {customers.map(customer => (
                        <label key={customer.id} className="customer-item">
                          <input
                            type="checkbox"
                            checked={selectedCustomers.includes(customer.id)}
                            onChange={() => handleCustomerToggle(customer.id)}
                          />
                          <span>{customer.name}</span>
                          <span className="email">{customer.email}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <button type="submit" className="primary" disabled={loading}>
                    {loading ? '发送中...' : `发送给 ${selectedCustomers.length} 个客户`}
                  </button>
                </form>
              </>
            )}

            {mode === 'send-whatsapp' && (
              <>
                <h2>💬 批量发送 WhatsApp</h2>
                <form onSubmit={handleSendWhatsApp}>
                  <div className="form-group">
                    <label>消息内容</label>
                    <textarea
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="输入 WhatsApp 消息..."
                      rows="6"
                    />
                  </div>

                  <div className="customer-selector">
                    <h3>选择收件客户 ({selectedCustomers.length})</h3>
                    <div className="customer-list">
                      {customers.map(customer => (
                        <label key={customer.id} className="customer-item">
                          <input
                            type="checkbox"
                            checked={selectedCustomers.includes(customer.id)}
                            onChange={() => handleCustomerToggle(customer.id)}
                          />
                          <span>{customer.name}</span>
                          <span className="phone">{customer.whatsapp || '无 WhatsApp'}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <button type="submit" className="primary" disabled={loading}>
                    {loading ? '发送中...' : `发送给 ${selectedCustomers.length} 个客户`}
                  </button>
                </form>
              </>
            )}

            {result && (
              <div className="result-panel">
                {result.error ? (
                  <div className="alert error">{result.error}</div>
                ) : (
                  <>
                    <div className="alert success">
                      ✓ 成功: {result.success_count} 个, 失败: {result.fail_count} 个
                    </div>
                    <div className="details">
                      {result.details?.map((detail, index) => (
                        <p key={index}>{detail}</p>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CommunicationsPage

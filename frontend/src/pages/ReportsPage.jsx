import React, { useState } from 'react'
import axios from 'axios'
import '../styles/ReportsPage.css'

function ReportsPage({ token }) {
  const [reportType, setReportType] = useState('customers')
  const [filters, setFilters] = useState({})
  const [loading, setLoading] = useState(false)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const handleExport = async (type) => {
    setLoading(true)
    try {
      let url = `/api/export/export-${type}`
      let method = 'POST'
      let config = { headers: { Authorization: `Bearer ${token}` } }

      if (type === 'sales-summary') {
        url = `/api/export/export-sales-summary?start_date=${startDate}&end_date=${endDate}`
        method = 'GET'
      }

      const response = await axios[method.toLowerCase()](
        url,
        type === 'sales-summary' ? undefined : filters,
        { ...config, responseType: 'blob' }
      )

      // 创建下载链接
      const url_link = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url_link
      link.setAttribute('download', `report_${new Date().getTime()}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.parentNode.removeChild(link)
    } catch (error) {
      alert('导出失败: ' + (error.response?.data?.error || error.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>📊 高级报表</h1>
      </div>

      <div className="reports-grid">
        {/* 客户报表 */}
        <div className="report-card card">
          <h2>👥 客户数据报表</h2>
          <p>导出所有客户信息为 Excel</p>

          <div className="form-group">
            <label>国家</label>
            <input
              type="text"
              placeholder="如：Egypt, Saudi Arabia"
              onChange={(e) =>
                setFilters({ ...filters, country: e.target.value })
              }
            />
          </div>

          <div className="form-group">
            <label>状态</label>
            <select
              onChange={(e) =>
                setFilters({ ...filters, status: e.target.value })
              }
            >
              <option value="">-- 全部 --</option>
              <option value="new">新客户</option>
              <option value="contacted">已联系</option>
              <option value="quoted">已报价</option>
              <option value="won">已成交</option>
            </select>
          </div>

          <div className="form-group">
            <label>客户等级</label>
            <select
              onChange={(e) => setFilters({ ...filters, grade: e.target.value })}
            >
              <option value="">-- 全部 --</option>
              <option value="A">A 级</option>
              <option value="B">B 级</option>
              <option value="C">C 级</option>
            </select>
          </div>

          <button
            className="primary"
            onClick={() => handleExport('customers')}
            disabled={loading}
          >
            {loading ? '导出中...' : '📥 导出 Excel'}
          </button>
        </div>

        {/* 报价报表 */}
        <div className="report-card card">
          <h2>💰 报价数据报表</h2>
          <p>导出所有报价信息为 Excel</p>

          <div className="form-group">
            <label>报价状态</label>
            <select
              onChange={(e) =>
                setFilters({ ...filters, status: e.target.value })
              }
            >
              <option value="">-- 全部 --</option>
              <option value="draft">草稿</option>
              <option value="sent">已发送</option>
              <option value="accepted">已接受</option>
              <option value="rejected">已拒绝</option>
            </select>
          </div>

          <div className="form-group">
            <label>产品类型</label>
            <select
              onChange={(e) =>
                setFilters({ ...filters, product_type: e.target.value })
              }
            >
              <option value="">-- 全部 --</option>
              <option value="Rooftop Unit">Rooftop Unit</option>
              <option value="Chiller">Chiller</option>
              <option value="AHU">AHU</option>
              <option value="FCU">FCU</option>
              <option value="VRF">VRF</option>
            </select>
          </div>

          <button
            className="primary"
            onClick={() => handleExport('quotations')}
            disabled={loading}
          >
            {loading ? '导出中...' : '📥 导出 Excel'}
          </button>
        </div>

        {/* 销售汇总 */}
        <div className="report-card card">
          <h2>📈 销售汇总报表</h2>
          <p>按时间范围统计销售数据</p>

          <div className="form-group">
            <label>开始日期</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>结束日期</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>

          <div className="date-preset">
            <button
              className="secondary"
              onClick={() => {
                const today = new Date()
                const lastMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
                setStartDate(lastMonth.toISOString().split('T')[0])
                setEndDate(today.toISOString().split('T')[0])
              }}
            >
              最近 30 天
            </button>
            <button
              className="secondary"
              onClick={() => {
                const today = new Date()
                const thisYear = new Date(today.getFullYear(), 0, 1)
                setStartDate(thisYear.toISOString().split('T')[0])
                setEndDate(today.toISOString().split('T')[0])
              }}
            >
              今年
            </button>
          </div>

          <button
            className="primary"
            onClick={() => handleExport('sales-summary')}
            disabled={loading || !startDate || !endDate}
          >
            {loading ? '导出中...' : '📥 导出 Excel'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ReportsPage

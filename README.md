# HVAC 外贸 CRM 系统

一个为暖通空调（HVAC）外贸销售打造的**轻量级、免费、开源** CRM 系统。

**核心功能：** 客户管理 + AI 智能话术 + 实时数据看板

---

## 🎯 功能概览

- ✅ **客户管理** - 导入、编辑、分类客户信息
- ✅ **AI 话术生成** - 根据客户国家、产品、阶段自动生成跟进话术
- ✅ **报价管理** - 管理报价、跟进计划
- ✅ **数据看板** - 实时销售漏斗、客户分布、转化率
- ✅ **客户分级** - AI 自动识别客户类型（经销商/EPC/终端）
- ✅ **跟进提醒** - 自动计算跟进时间、生成跟进计划

---

## 🚀 快速开始

### 前提条件
- Docker & Docker Compose
- Git

### 安装和运行（一键启动）

```bash
# 1. 克隆仓库
git clone https://github.com/engy001/hvac-crm.git
cd hvac-crm

# 2. 一键启动（Docker）
docker-compose up --build

# 3. 打开浏览器
# 前端: http://localhost:3000
# 后端 API: http://localhost:5000
```

### 不用 Docker？本地运行

**后端：**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**前端（新终端）：**
```bash
cd frontend
npm install
npm run dev
```

---

## 📊 系统架构

```
┌─────────────┐
│  前端 (React)    │  http://localhost:3000
└────────┬────────┘
         │
         │ REST API
         │
┌────────▼────────┐
│ 后端 (Flask)     │  http://localhost:5000
├──────────────────┤
│ 客户管理 API     │
│ 报价 API         │
│ AI 话术 Agent    │
│ 数据看板 API     │
└────────┬────────┘
         │
┌────────▼────────┐
│ 数据库 (SQLite) │
└──────────────────┘
```

---

## 🤖 AI Agent 说明

CRM 内置 **3 个核心 AI Agent**：

### 1. **客户身份识别 Agent**
- 输入：公司介绍、采购产品、国家、邮箱类型
- 输出：客户类型（经销商/EPC/终端/贸易商）+ 置信度 + 建议

### 2. **跟进话术生成 Agent**
- 输入：客户国家、产品、当前阶段、客户类型
- 输出：本地化 WhatsApp/邮件话术

### 3. **阶段判断 Agent**
- 输入：报价日期、是否回复、最后沟通内容
- 输出：当前阶段（比价/技术确认/项目未启动/暂停）+ 30天跟进计划

---

## 📱 主要界面

### 客户管理
- 列表/卡片视图
- 快速搜索、筛选、排序
- 批量导入（CSV）
- 客户详情、编辑、删除

### AI 话术生成器
```
输入：
- 国家（非洲/中东/拉美/中亚）
- 产品（Rooftop Unit/Chiller/AHU/等）
- 阶段（报价后/技术确认/项目启动）
- 客户类型（可选）

输出：
- WhatsApp 话术
- 邮件版话术
- 多语言支持
```

### 数据看板
- 总客户数、活跃客户
- 销售漏斗（询盘→报价→成交）
- 国家分布 TOP 10
- 产品热度排行
- 近 30 天转化率

---

## 🔧 配置 AI API

### 方式 1：使用 OpenAI API（推荐快速）

1. 获得 OpenAI API Key: https://platform.openai.com/api-keys
2. 修改 `backend/.env`:

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

### 方式 2：使用本地免费 LLM（推荐离线）

使用 **Ollama** + **Llama 2 / Mistral**（完全免费、离线）

```bash
# 安装 Ollama: https://ollama.ai
ollama pull mistral  # 或 llama2

# 修改 backend/.env
USE_LOCAL_LLM=true
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 📁 项目结构

```
hvac-crm/
├── backend/
│   ├── app.py                    # Flask 主应用
│   ├── models.py                 # SQLAlchemy 模型
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── customers.py          # 客户 CRUD
│   │   ├── quotations.py         # 报价管理
│   │   ├── ai_agents.py          # AI 话术 API
│   │   └── dashboard.py          # 看板数据
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── customer_identifier.py    # 客户识别
│   │   ├── followup_generator.py     # 话术生成
│   │   └── stage_analyzer.py         # 阶段分析
│   ├── database.db               # SQLite 数据库（自动创建）
│   ├── .env                      # 环境变量
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-entrypoint.sh
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── CustomerList.jsx
│   │   │   ├── CustomerForm.jsx
│   │   │   ├── AIDialog.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── QuotationForm.jsx
│   │   ├── pages/
│   │   │   ├── CustomersPage.jsx
│   │   │   ├── AIPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── .dockerignore
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🔐 安全建议

- 本地数据库（SQLite）不适合生产环境，建议升级到 PostgreSQL
- 修改 `backend/app.py` 中的 `SECRET_KEY`
- 添加用户认证（可选）
- 定期备份 `database.db` 文件

---

## 📈 下一步扩展

- [ ] 用户认证和权限管理
- [ ] 多语言支持（英文/中文/阿拉伯文等）
- [ ] 邮件/WhatsApp 集成（自动发送话术）
- [ ] 高级报表导出（Excel/PDF）
- [ ] 移动应用版本
- [ ] 与阿里巴巴/LinkedIn 的 API 集成

---

## 💡 使用技巧

### 批量导入客户
```csv
公司名称,国家,邮箱,电话,客户类型,行业
ABC Company,埃及,info@abc.com,+20123456789,经销商,HVAC
```

### 生成跟进计划
1. 选择一个客户
2. 点击"生成跟进计划"
3. 选择产品和当前阶段
4. AI 自动生成 30 天计划和话术

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

## 📄 许可证

MIT License - 完全免费使用

---

## 📞 支持

有问题？提交 Issue 或联系开发者

---

**祝你销售业绩翻倍！** 🚀

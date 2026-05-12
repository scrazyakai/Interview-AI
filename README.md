# Interview AI · AI 模拟面试平台

> 基于豆包大模型的智能面试练习平台，支持实时语音对话与简历智能解析，帮助求职者在真实面试前充分热身。

---

## 项目简介

Interview AI 是一个全栈 AI 面试模拟系统。用户上传简历、选择目标岗位和面试难度后，系统调用豆包大模型扮演面试官，通过实时语音或文字对话模拟真实面试场景，完整记录每次练习的对话历史，帮助用户发现自身薄弱点、积累面试经验。

---

## 技术栈

**后端**

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI + Uvicorn |
| 数据库 | PostgreSQL + asyncpg |
| ORM | SQLAlchemy (async) |
| 认证 | JWT (python-jose + bcrypt) |
| 实时通信 | WebSocket |
| LLM 集成 | 豆包大模型 / Qwen / LangChain |
| PDF 解析 | pdfplumber |
| 配置管理 | pydantic-settings |

**前端**

| 类别 | 技术 |
|------|------|
| 框架 | Vue 3 + TypeScript |
| 路由 | Vue Router |
| 状态管理 | Pinia |
| 样式 | Tailwind CSS |
| 构建工具 | Vite |

---

## 已完成功能

### 用户系统
- [x] 用户注册 / 登录，JWT 无状态认证
- [x] 注册自动赠送 200 积分
- [x] 个人中心页面（用户信息、积分余额、积分明细分页）

### 面试核心
- [x] 面试参数配置（目标岗位、JD、简历文本、难度、模式）
- [x] 实时语音面试（WebSocket + 豆包 ASR / TTS / LLM 三合一）
- [x] 文字对话面试
- [x] 多难度支持：初级 / 中级 / 高级
- [x] 多模式支持：技术面 / 行为面 / 综合面
- [x] 面试对话历史完整持久化

### 简历模块
- [x] PDF 简历上传与文本提取（pdfplumber）
- [x] LLM 自动解析简历结构（姓名、邮箱、电话、技能、工作经历、教育经历）
- [x] 解析结果结构化存储（resumes / resume_work_experiences / resume_educations 三张表）
- [x] 解析失败 3 次自动重试，有明确错误提示

### 工程基础
- [x] 统一 ApiResponse 响应格式
- [x] 自定义业务异常（BizException + ErrorCode）
- [x] 全局异常处理器
- [x] 结构化日志系统（请求追踪 + SQL 耗时记录）
- [x] 模块化分层架构（API → Service → CRUD → Model）

---

## 未来规划

### 近期
- [ ] 简历在线编辑（工作经历 / 教育经历的增删改）
- [ ] 面试结束后生成 AI 点评报告（评分 + 优劣势分析 + 改进建议）
- [ ] 面试历史列表页，支持回放完整对话记录

### 中期
- [ ] RAG 题库系统：接入 PGVector，将行业高频题库向量化，面试时动态检索注入上下文，提升提问质量与针对性
- [ ] 积分消耗机制：每次面试按时长或轮次扣积分，引导用户付费充值
- [ ] 支付模块接入（积分充值 / 会员订阅）
- [ ] 用户数据看板：历史面试评分趋势图、薄弱技能标签云

### 长期
- [ ] 英文面试模式（多语言支持）
- [ ] 企业端：HR 可创建定制化题库，生成专属面试链接邀请候选人练习
- [ ] 面试视频录制与回放

---

## 快速开始

**环境要求**：Python 3.12+、Node.js 20+、PostgreSQL 15+

### 1. 安装依赖

```bash
# 后端依赖
uv sync

# 前端依赖
cd frontend && npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
python generate_secret_key.py  # 生成 JWT 密钥
```

编辑 `.env`，填写以下必需配置：

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | PostgreSQL 连接字符串 |
| `JWT_SECRET_KEY` | 上一步生成的密钥 |
| `VOLC_REALTIME_APP_ID` | 豆包实时语音 App ID |
| `VOLC_REALTIME_ACCESS_KEY` | 豆包实时语音 Access Key |
| `VOLC_API_KEY` | 豆包文本模型 API Key |
| `QWEN_API_KEY` | Qwen API Key（简历解析） |

```bash
python check_config.py  # 验证配置是否完整
```

### 3. 启动服务

```bash
# 后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端（新终端）
cd frontend && npm run dev
```

访问 http://localhost:5173 开始使用，API 文档见 http://localhost:8000/docs。

---

## 项目结构

```
interviwew-ai/
├── app/
│   ├── api/            # 路由层（auth / user / interview / resume）
│   ├── services/       # 业务逻辑层
│   ├── crud/           # 数据库操作层
│   ├── models/         # SQLAlchemy ORM 模型
│   ├── schemas/        # Pydantic 数据模型
│   ├── core/           # 配置、日志、异常处理
│   └── db/             # 数据库连接与 Session 管理
└── frontend/
    └── src/
        ├── views/      # 页面组件
        ├── components/ # 复用组件
        ├── router/     # 路由配置
        └── utils/      # 工具函数（认证等）
```

---

## 安全提示

- 不要将 `.env` 文件提交到版本控制系统
- 生产环境必须使用强随机密钥，并定期更换 JWT 密钥
- 生产部署请使用 HTTPS，并限制 CORS 允许的域名

---

## License

MIT

# AI Agent Skill Validator

AI Agent Skill 自动化校验和评估平台。

## 功能特性

- ✅ 用户认证系统（JWT）
- 📤 Skill 压缩包上传（.zip / .tar.gz）
- 🔍 结构校验（SKILL.md 格式验证）
- 📊 双引擎评估：
  - 技术得分（50%）：工具能力、工程质量、逻辑大脑、RAG 检索
  - AI 表现分（50%）：任务达成率、指令遵循度、抗干扰能力、Token 消耗效率
- 📝 多格式评分报告（JSON/HTML/Markdown）

## 技术栈

### 后端
- FastAPI
- PostgreSQL
- Redis
- Celery

### 前端
- Vue.js 3
- Vite
- Element Plus
- ECharts

## 快速开始

### 环境要求

- Docker & Docker Compose
- Node.js 18+ (本地开发)
- Python 3.11+ (本地开发)

### Docker 部署

1. 克隆项目：
```bash
git clone https://github.com/your-username/ai-agent-skill-validator.git
cd ai-agent-skill-validator
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

3. 启动服务：
```bash
docker-compose up -d
```

4. 访问应用：
- 前端：http://localhost
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 本地开发

#### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 前端
```bash
cd frontend
npm install
npm run dev
```

#### 启动 Celery Worker
```bash
cd backend
celery -A tasks.celery_app worker --loglevel=info
```

## API 接口

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### Skills
- `POST /api/skills/upload` - 上传 Skill
- `GET /api/skills/` - 获取 Skill 列表
- `GET /api/skills/{id}` - 获取 Skill 详情
- `GET /api/skills/{id}/report/json` - 获取 JSON 报告
- `GET /api/skills/{id}/report/html` - 获取 HTML 报告
- `GET /api/skills/{id}/report/markdown` - 获取 Markdown 报告
- `DELETE /api/skills/{id}` - 删除 Skill

## Skill 包结构

```
my-skill/
├── SKILL.md          # 必需：技能定义文件
├── skill.py          # 可选：Python 实现代码
├── requirements.txt  # 可选：Python 依赖
└── README.md         # 可选：说明文档
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| SECRET_KEY | JWT 密钥 | your-secret-key-change-in-production |
| DATABASE_URL | 数据库连接 | postgresql://postgres:postgres@localhost:5432/skill_validator |
| REDIS_URL | Redis 连接 | redis://localhost:6379/0 |
| OPENAI_API_KEY | OpenAI API Key | - |
| OPENAI_BASE_URL | OpenAI API Base URL | https://api.openai.com/v1 |
| OPENAI_MODEL | OpenAI 模型 | gpt-4 |

## License

MIT

# Hot Knowledge Sharing Website (Noosphere) - AI Agent Context

> 此文件包含项目架构、技术栈、代码规范和开发指南，供 AI 编码助手参考。

---

## 项目概述

**项目名称**: Hot Knowledge Sharing Website (代号: Noosphere)  
**类型**: 知识分享社交平台  
**架构**: 前后端分离 (Frontend + Backend + Database)

### 核心特性
- 用户认证系统（注册/登录/登出/密码重置）
- JWT 无状态认证
- 邮箱验证（OTP 验证码）
- 可折叠侧边栏导航（展开/图标两种模式）
- 毛玻璃视觉效果（Glassmorphism）
- 响应式设计 + 暗色主题支持

---

## 技术栈

| 层级 | 技术 | 版本/备注 |
|------|------|-----------|
| 前端 | Vue 3 + Composition API | Vite 构建工具 |
| 路由 | Vue Router 4 | 前端路由守卫 |
| 后端 | Flask + Flask-RESTful | Python 3.x |
| 数据库 | PostgreSQL | psycopg v3 驱动 |
| 认证 | JWT (PyJWT) | HS256 算法 |
| 密码 | Werkzeug | 自动加盐哈希 |

---

## 项目结构

```
.
├── website-frontend/          # Vue 3 前端项目
│   ├── src/
│   │   ├── pages/             # 页面组件
│   │   │   ├── LoginPage.vue      # 登录页（双栏布局）
│   │   │   ├── Register.vue       # 注册页
│   │   │   ├── ForgotPasswordPage.vue  # 忘记密码
│   │   │   └── HomePage.vue       # 主页（核心功能）
│   │   ├── components/        # 可复用组件
│   │   │   ├── LayoutShell.vue    # 布局外壳
│   │   │   └── Card.vue
│   │   ├── services/          # API 封装
│   │   │   ├── auth.js            # 认证相关 API
│   │   │   └── http.js            # HTTP 请求基类
│   │   ├── router/            # 路由配置
│   │   │   └── index.js
│   │   ├── styles/            # 样式变量
│   │   │   └── variables.css      # CSS 变量（主题色）
│   │   ├── config/            # 配置文件
│   │   │   └── env.js             # 环境变量
│   │   ├── App.vue            # 根组件
│   │   ├── main.js            # 入口文件
│   │   └── style.css          # 全局样式
│   ├── index.html             # HTML 模板
│   ├── package.json
│   └── vite.config.js         # Vite 配置（含代理）
│
├── website-backend/           # Flask 后端项目
│   ├── app/
│   │   ├── resources/         # RESTful 资源
│   │   │   └── auth_resources/
│   │   │       ├── __init__.py
│   │   │       ├── login_resource.py
│   │   │       ├── register_resource.py
│   │   │       ├── logout_resource.py
│   │   │       ├── email_verify_resource.py
│   │   │       └── reset_password_resource.py
│   │   ├── auth/              # 认证模块
│   │   │   ├── __init__.py
│   │   │   ├── jwt.py             # JWT 创建/解码
│   │   │   ├── passwords.py       # 密码哈希
│   │   │   ├── middleware.py      # @require_auth 装饰器
│   │   │   └── validation.py      # 输入验证（用户名/密码/邮箱）
│   │   ├── db/                # 数据库模块
│   │   │   ├── __init__.py
│   │   │   ├── connection.py      # 数据库连接
│   │   │   ├── migration.py       # 迁移管理
│   │   │   ├── user_info_model.py # 表名常量
│   │   │   └── user_schema_migration.py  # 迁移 SQL
│   │   ├── common_func/       # 通用函数
│   │   │   ├── __init__.py
│   │   │   ├── api.py             # API 工厂
│   │   │   └── validation.py      # JSON 验证
│   │   ├── routes.py          # 路由注册
│   │   └── security/          # 安全相关
│   ├── conf/                  # 配置文件
│   │   ├── __init__.py
│   │   ├── global.conf            # 主配置文件（INI 格式）
│   │   ├── config.py              # Config 类
│   │   └── load_global_conf.py    # 配置加载逻辑
│   ├── scripts/               # 实用脚本
│   │   ├── init_db.py             # 数据库初始化
│   │   └── pg_snapshot.py         # PostgreSQL 备份/恢复
│   ├── backups/               # 自动备份目录
│   ├── requirements.txt       # Python 依赖
│   └── run.py                 # 后端入口文件
│
└── docs/                      # 文档
    └── 开发环境配置指南.md
```

---

## 端口与服务

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端开发服务器 | 15001 | Vite dev server |
| 后端 API 服务 | 15000 | Flask 应用 |
| 前端代理 | /api -> :15000 | vite.config.js 配置 |

---

## 常用命令

### 前端
```bash
cd website-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 后端
```bash
cd website-backend

# 激活虚拟环境
source ../.venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate      # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务
python run.py

# 环境变量覆盖
FLASK_RUN_HOST=0.0.0.0 FLASK_RUN_PORT=15000 python run.py
```

### 数据库
```bash
# 初始化数据库（重置并创建 admin 用户）
python website-backend/scripts/init_db.py --yes

# 导出数据库快照
python website-backend/scripts/pg_snapshot.py export --out backup.sql

# 导入数据库快照
python website-backend/scripts/pg_snapshot.py import --in backup.sql
```

---

## 配置系统

配置优先级（从高到低）：
1. `conf/global.conf` 文件中的值
2. 环境变量
3. 代码中的默认值

### global.conf 示例
```ini
[flask]
debug = 0
secret_key = dev-secret-change-me
json_sort_keys = false

[postgres]
user = boriszhang
password =
host = localhost
port = 5432
db = hot_knowledge
```

### 环境变量
- `FLASK_DEBUG`: 开启调试模式
- `SECRET_KEY`: JWT 签名密钥
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`: 数据库连接

---

## 认证系统

### JWT Token
- **算法**: HS256
- **有效期**: 7 天（7 * 24 * 60 * 60 秒）
- **存储**: 前端 localStorage (`access_token`)
- **传输**: `Authorization: Bearer <token>` 请求头

### 密码规则
- 最少 8 个字符
- 至少 1 个大写字母
- 至少 1 个小写字母
- 至少 1 个数字

### 用户名规则
- 3-30 个字符
- 只能包含字母、数字和下划线
- 必须以字母开头

### 邮箱验证
- 首次登录或 7 天未登录需要邮箱验证
- OTP 验证码 10 分钟有效期（开发模式直接返回）
- 内存存储（重启后清空）

---

## 数据库设计

### user_info 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGSERIAL PRIMARY KEY | 自增主键 |
| username | TEXT UNIQUE | 用户名 |
| password_hash | TEXT | 密码哈希（werkzeug） |
| email | TEXT UNIQUE | 邮箱地址 |
| is_active | BOOLEAN DEFAULT TRUE | 账户激活状态 |
| email_verified | BOOLEAN DEFAULT FALSE | 邮箱验证状态 |
| last_login_at | TIMESTAMPTZ | 最后登录时间 |
| created_at | TIMESTAMPTZ DEFAULT NOW() | 创建时间 |

### 索引
- `idx_user_info_username` on username
- `idx_user_info_email` on email

### 迁移系统
- 版本号管理（schema_migrations 表）
- 自动执行未应用的迁移
- 支持幂等性（多次运行安全）

---

## API 端点

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST | /api/auth/register | 用户注册 | 否 |
| POST | /api/auth/login | 用户登录 | 否 |
| POST | /api/auth/logout | 用户登出 | 是 |
| POST | /api/auth/email_verifying | 发送验证码 | 否 |
| POST | /api/auth/reset_success | 重置密码 | 否 |
| GET | / | 应用信息 | 否 |
| GET | /healthz | 健康检查 | 否 |
| GET | /db/health | 数据库健康检查 | 否 |

---

## 前端架构

### 路由守卫
```javascript
router.beforeEach((to, _from, next) => {
  if (to.meta.requiresAuth && !localStorage.getItem('access_token')) {
    next('/login')
  } else {
    next()
  }
})
```

### 本地存储键
- `access_token`: JWT Token
- `username`: 当前用户名
- `hk_sidebar_collapsed`: 侧边栏折叠状态（'0' 或 '1'）
- `hk_browsing_history`: 浏览历史（JSON 数组）

### 样式系统
CSS 变量定义在 `src/styles/variables.css`：
- `--bg`: 背景色
- `--bg-elev`:  elevated 背景色
- `--text`: 文字颜色
- `--brand`: 品牌主色（蓝色）
- `--border`: 边框颜色
- `--radius-*`: 圆角大小
- `--space-*`: 间距单位

支持暗色模式（`prefers-color-scheme: dark`）

---

## 代码规范

### Python
- 使用 `from __future__ import annotations` 启用类型注解
- 函数添加类型注解和 Google 风格 docstring
- 常量使用 `Final` 类型标注
- 使用 f-string 进行字符串格式化

### JavaScript/Vue
- 使用 Composition API (`<script setup>`)
- 组件名使用 PascalCase
- 文件路径使用相对路径
- 使用 CSS 变量管理主题色

---

## 安全注意事项

1. **Token 黑名单**: 当前为内存存储（重启清空），生产环境建议使用 Redis
2. **OTP 存储**: 当前为内存存储（重启清空），10 分钟过期
3. **密码哈希**: 使用 werkzeug 自动生成 salt
4. **CORS**: 开发环境无限制，生产环境需配置
5. **配置文件中不要提交真实密码**: `global.conf` 已包含敏感信息，确保不提交到 Git

---

## 测试策略

当前项目暂无自动化测试，建议添加：
- 后端：pytest + Flask test client
- 前端：Vitest + Vue Test Utils

---

## 开发注意事项

1. **虚拟环境**: 所有 Python 操作应在 `.venv` 中进行
2. **数据库连接**: 确保 PostgreSQL 服务已启动
3. **首次运行**: 执行 `python website-backend/scripts/init_db.py --yes` 初始化数据库
4. **前端代理**: Vite 自动将 `/api/*` 代理到 `:15000`
5. **代码修改**: 后端修改需重启服务，前端修改自动热更新

---

## 相关文档

- `docs/开发环境配置指南.md` - 环境搭建详细说明（PostgreSQL、Node.js 安装等）

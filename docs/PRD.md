# 智学助手 · 产品需求文档（PRD）

**版本**: v1.0
**日期**: 2026-03-03
**作者**: 产品经理
**状态**: 已实现

---

## 一、产品概述

### 1.1 产品定位

智学助手是一款面向学生的 AI 驱动学习辅助系统，通过智能问答、个人知识库、学情分析等功能，提供个性化学习支持。

### 1.2 核心价值

- **智能问答**：基于大语言模型的自然语言交互
- **知识库 RAG**：上传个人资料，获得精准个性化答案
- **学情分析**：自动调用工具查询学习数据，生成分析报告
- **多模态支持**：文本、图片、PDF 混合输入

### 1.3 技术架构

- **前端**: Vue 3 + TypeScript + Vite + Pinia
- **后端**: FastAPI + SQLAlchemy (async) + SQLite
- **A I**: DeepSeek API (chat + embeddings)
- **通信**: SSE 流式响应

---

## 二、用户角色

| 角色 | 描述 | 权限 |
|------|------|------|
| 学生 | 主要用户 | 问答、知识库管理、学情查询 |
| 管理员 | 系统维护者（未实现） | 用户管理、系统配置 |

---

## 三、功能需求

### 3.1 智能问答

#### 用户故事
> 作为学生，我希望用自然语言提问并获得 AI 实时流式回答，以便快速解决学习疑问。

#### 功能描述

用户在输入框输入问题，系统调用 AI 模型生成回答，以流式方式逐字输出。支持多轮对话、工具调用、Markdown 渲染。

#### 输入规范

| 字段 | 类型 | 必填 | 说明 | 限制 |
|------|------|------|------|------|
| message | string | 是 | 用户消息 | 1-10000 字符 |
| conversation_id | string | 否 | 对话 ID | UUID 格式，不传则新建 |
| attachment_ids | string[] | 否 | 附件 ID 列表 | 最多 5 个 |
| kb_ids | object[] | 否 | 知识库列表 | `[{id, name}]` |
| model | string | 否 | 模型 ID | `deepseek-chat` \| `deepseek-reasoner` |

#### 输出规范

SSE 事件流，格式：`data: {JSON}\n\n`

**事件类型**：

| type | 说明 | 字段 |
|------|------|------|
| conversation_id | 对话 ID | content: string |
| tool_call | 工具调用 | tool_name: string, tool_args: object |
| tool_result | 工具结果 | tool_name: string, content: string |
| text | 流式文本 | content: string |
| done | 完成标记 | - |

#### 验收标准

**正常流程**：
- [x] 输入 1-10000 字符消息，Enter 发送
- [x] 回答以流式方式输出，延迟 < 3s
- [x] Markdown 正确渲染（加粗、列表、代码块）
- [x] LaTeX 公式正确渲染（行内 `$...$`，块级 `$$...$$`）
- [x] 工具调用显示加载状态
- [x] 对话历史自动保存

**边界条件**：
- [ ] 空消息：禁用发送按钮
- [ ] 超长消息（>10000字符）：前端截断并提示
- [ ] 流式中断：显示错误提示，允许重试
- [ ] 无网络：显示连接失败，不保存消息

**异常处理**：
- [ ] 后端 500 错误：显示"服务异常，请稍后重试"
- [ ] 超时（>60s）：自动断开，提示用户
- [ ] API Key 失效：返回明确错误信息

#### API 接口

```
POST /api/chat/stream
Content-Type: application/json

Request:
{
  "message": "解释一下牛顿第一定律",
  "conversation_id": "uuid-xxx",
  "attachment_ids": ["att-1"],
  "kb_ids": [{"id": "kb-1", "name": "物理笔记"}],
  "model": "deepseek-chat"
}

Response: (SSE)
data: {"type":"conversation_id","content":"uuid-xxx"}

data: {"type":"text","content":"牛顿"}

data: {"type":"text","content":"第一定律"}

data: {"type":"done"}
```

---

### 3.2 模型切换

#### 用户故事
> 作为学生，我希望根据问题类型选择不同模型，在速度和推理深度间灵活切换。

#### 功能描述

提供两个模型选项，用户可在输入框工具栏切换。

#### 模型列表

| 模型 ID | 显示名称 | 描述 | 适用场景 |
|---------|----------|------|----------|
| deepseek-chat | DeepSeek V3.2 | 快速通用，适合日常问答 | 知识查询、简单计算 |
| deepseek-reasoner | DeepSeek R2 | 深度推理，适合复杂分析 | 数学证明、逻辑推理 |

#### 验收标准

**正常流程**：
- [x] 首页和对话页均显示模型选择器
- [x] 点击显示下拉菜单，含模型名称和描述
- [x] 选中模型高亮显示 ✓
- [x] 切换后立即生效，下次发送使用新模型

**边界条件**：
- [x] 默认选中 DeepSeek V3.2
- [x] 切换不影响当前对话历史
- [x] 刷新页面保持选择（localStorage）

---

### 3.3 知识库管理

#### 用户故事
> 作为学生，我希望上传学习资料构建个人知识库，让 AI 基于我的资料回答问题。

#### 功能描述

用户创建知识库，上传文件，系统自动解析、分块、向量化。支持预览、查看知识块、删除。

#### 3.3.1 创建知识库

**输入规范**：

| 字段 | 类型 | 必填 | 说明 | 限制 |
|------|------|------|------|------|
| name | string | 是 | 知识库名称 | 1-50 字符 |
| description | string | 否 | 描述 | 0-200 字符 |
| tags | object[] | 否 | 标签 | `[{category, value}]` |

**标签分类**：

- 行业：教育、医疗、金融、科技、法律、制造、零售
- 专业：计算机、数学、物理、化学、生物、历史、语文、英语
- 学科：理科、文科、工科、艺术
- 难度：入门、初级、中级、高级

**验收标准**：
- [x] 名称必填，1-50 字符
- [x] 描述可选，最多 200 字符
- [x] 标签可多选，每个分类最多选 1 个
- [x] 创建成功后显示在列表顶部

**边界条件**：
- [x] 名称为空：禁用创建按钮
- [x] 名称重复：允许（通过 ID 区分）
- [x] 无标签：允许创建

**API 接口**：

```
POST /api/knowledge/bases
Content-Type: application/json

Request:
{
  "name": "高中物理笔记",
  "description": "高一到高三物理知识点整理",
  "tags": [
    {"category": "专业", "value": "物理"},
    {"category": "难度", "value": "中级"}
  ]
}

Response:
{
  "id": "kb-uuid",
  "name": "高中物理笔记",
  "description": "...",
  "tags": [...],
  "created_at": "2026-03-03T10:00:00Z"
}
```

#### 3.3.2 上传文档

**输入规范**：

| 字段 | 类型 | 必填 | 说明 | 限制 |
|------|------|------|------|------|
| kb_id | string | 是 | 知识库 ID | UUID 格式 |
| file | File | 是 | 文件对象 | 见文件类型限制 |

**文件类型限制**：

| 类型 | MIME Type | 扩展名 | 大小限制 |
|------|-----------|--------|----------|
| PDF | application/pdf | .pdf | 50MB |
| 图片 | image/jpeg, image/png, image/webp | .jpg, .png, .webp | 10MB |
| Excel | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet | .xlsx, .xls | 20MB |

**处理流程**：

1. 文件上传 → 保存到 `uploads/knowledge/{kb_id}/{doc_id}.ext`
2. 创建文档记录，状态 = `pending`
3. 后台任务：解析 → 分块 → 向量化
4. 状态更新：`processing` → `done` / `error`

**分块规则**：

- 块大小：500 字符
- 重叠：50 字符
- 向量模型：`text-embedding-v3`

**验收标准**：

**正常流程**：
- [x] 选择文件后显示文件名
- [x] 上传中显示"上传中..."
- [x] 上传成功后文档出现在列表，状态"等待处理"
- [x] 2-10s 后状态变为"处理中..."
- [x] 处理完成后状态变为"已完成 · N 块"

**边界条件**：
- [x] 不支持的文件类型：提示"不支持的文件类型: xxx"
- [x] 文件过大：前端限制，超过限制不允许选择
- [x] 知识库不存在：返回 404
- [x] 同名文件：允许（通过 ID 区分）

**异常处理**：
- [ ] 解析失败：状态显示"处理失败"，可删除重传
- [ ] 向量化失败：chunk 的 embedding 字段为 null，不影响其他 chunk
- [ ] 网络中断：上传失败，提示重试

**API 接口**：

```
POST /api/knowledge/bases/{kb_id}/upload
Content-Type: multipart/form-data

Request:
file: (binary)

Response:
{
  "id": "doc-uuid",
  "file_name": "物理公式.pdf",
  "file_type": "pdf",
  "status": "pending"
}
```

#### 3.3.3 文档预览

**验收标准**：
- [ ] PDF：iframe 直接展示
- [ ] 图片：img 标签展示
- [ ] Excel：显示纯文本内容（Sheet 名 + 表格数据）
- [ ] 点击"关闭"按钮关闭预览

**边界条件**：
- [ ] 文档不存在：返回 404
- [ ] 文件已删除：返回 404
- [ ] 不支持预览的类型：返回 400

#### 3.3.4 知识块查看

**验收标准**：
- [ ] 左侧导航显示所有块，格式"# N · X 字"
- [ ] 点击块后右侧显示完整内容
- [ ] 当前块高亮显示
- [ ] 默认选中第一块

**边界条件**：
- [ ] 无知识块：显示"暂无知识块"
- [ ] 块内容为空：显示"（空）"

---

### 3.4 知识库问答（RAG）

#### 用户故事
> 作为学生，我希望在对话时关联知识库，让 AI 基于我的资料回答，获得精准个性化答案。

#### 功能描述

用户在输入框选择知识库，发送消息时 AI 自动判断是否需要检索，检索后基于结果回答。

#### 检索规则

- **触发条件**：智能体判断问题与知识库相关
- **检索方式**：用户问题向量化 → 余弦相似度排序
- **相似度阈值**：≥ 0.3
- **返回数量**：top_k = 5（可调）

#### 验收标准

**正常流程**：
- [ ] 输入框显示"知识库"按钮，点击弹出下拉
- [ ] 可多选知识库，显示选中数量
- [ ] 发送消息时 kb_ids 传给后端
- [ ] AI 自动调用 search_knowledge_base 工具
- [ ] 回答中引用知识库内容

**边界条件**：
- [ ] 未选知识库：不调用检索工具
- [ ] 知识库为空：返回"未找到相关内容"
- [ ] 相似度 < 0.3：不返回结果
- [ ] 多个知识库：分别检索，合并结果

**异常处理**：
- [ ] 知识库不存在：跳过该知识库
- [ ] 向量化失败：返回空结果
- [ ] 检索超时：返回部分结果

---

### 3.5 学情工具

#### 功能描述

AI 智能体可调用 10 个内置工具查询学生数据、生成学习内容。

#### 工具列表

| 工具名 | 描述 | 参数 | 返回 |
|--------|------|------|------|
| get_attendance_records | 查询考勤记录 | student_id, date_range | 考勤列表 |
| get_learning_status | 查询学习状态 | student_id | 各科成绩、进度 |
| get_task_progress | 查询任务进度 | student_id | 作业完成情况 |
| get_knowledge_mastery | 查询知识点掌握度 | student_id, subject | 知识点列表 + 掌握度 |
| web_search | 联网搜索 | query | 搜索结果摘要 |
| solve_math_problem | 数学计算 | expression | 计算结果 + 步骤 |
| generate_practice_problems | 生成练习题 | subject, difficulty, count | 题目列表 |
| create_study_plan | 制定学习计划 | subject, weak_points, duration | 学习计划 |
| explain_concept | 讲解知识点 | concept, level | 讲解内容 |
| search_knowledge_base | 知识库检索 | kb_id, query, top_k | 相关内容列表 |

#### 验收标准

**正常流程**：
- [ ] 用户提问"我最近学得怎么样"
- [ ] AI 自动调用 get_learning_status
- [ ] 显示工具调用状态
- [ ] 基于工具结果生成回答

**边界条件**：
- [ ] 工具参数缺失：AI 自动补充默认值
- [ ] 工具返回空：AI 提示"暂无数据"
- [ ] 多工具联动：按顺序执行

**异常处理**：
- [ ] 工具执行失败：返回错误信息，AI 继续回答
- [ ] 超时：跳过该工具
- [ ] 最多 5 轮工具调用，防止死循环

---

### 3.6 文件附件

#### 用户故事
> 作为学生，我希望在对话中上传图片或 PDF，让 AI 直接分析文件内容。

#### 功能描述

用户点击附件按钮上传文件，系统解析后随消息一起发送给 AI。

#### 输入规范

| 字段 | 类型 | 限制 |
|------|------|------|
| file | File | 图片: 5MB, PDF: 20MB |
| 数量 | - | 最多 5 个 |

#### 验收标准

**正常流程**：
- [ ] 点击附件按钮选择文件
- [ ] 上传中显示"上传中..."
- [ ] 上传成功显示文件名 chip
- [ ] 点击 × 删除附件
- [ ] 发送时附件内容注入消息

**边界条件**：
- [ ] 图片：转 base64，多模态输入
- [ ] PDF：提取文本，拼接到消息
- [ ] 超过 5 个：禁用上传按钮

**异常处理**：
- [ ] 上传失败：提示重试
- [ ] 解析失败：跳过该附件

---

## 四、非功能需求

### 4.1 性能要求

| 指标 | 要求 |
|------|------|
| 首字符延迟 | ≤ 3s |
| 流式输出速度 | ≥ 20 字符/秒 |
| 文件上传速度 | ≥ 1MB/s |
| 知识库检索 | ≤ 2s |
| 页面加载 | ≤ 2s |

### 4.2 可用性要求

- 7×24 小时可用
- 月度可用率 ≥ 99%
- 故障恢复时间 ≤ 1 小时

### 4.3 安全要求

- CORS 限制来源（默认 localhost:5173）
- 文件类型白名单校验
- SQL 注入防护（使用 ORM）
- XSS 防护（前端转义）

### 4.4 兼容性要求

- 浏览器：Chrome 90+, Safari 14+, Firefox 88+
- 屏幕：≥ 1280×720
- 移动端：暂不支持

---

## 五、数据模型

### 5.1 对话表 (conversations)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| title | String | 对话标题 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 5.2 消息表 (messages)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| conversation_id | UUID | 外键 |
| role | Enum | user \| assistant \| system \| tool |
| content | Text | 消息内容 |
| created_at | DateTime | 创建时间 |

### 5.3 知识库表 (knowledge_bases)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| name | String(50) | 名称 |
| description | String(200) | 描述 |
| tags | JSON | 标签数组 |
| created_at | DateTime | 创建时间 |

### 5.4 文档表 (knowledge_documents)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| kb_id | UUID | 外键 |
| file_name | String | 文件名 |
| file_type | Enum | pdf \| image \| excel |
| file_path | String | 文件路径 |
| status | Enum | pending \| processing \| done \| error |
| chunk_count | Integer | 知识块数量 |
| created_at | DateTime | 创建时间 |

### 5.5 知识块表 (knowledge_chunks)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| doc_id | UUID | 外键 |
| kb_id | UUID | 外键 |
| chunk_index | Integer | 块索引 |
| content | Text | 文本内容 |
| embedding | JSON | 向量（float[]） |

---

## 六、待规划功能

| 功能 | 优先级 | 说明 | 预计工作量 |
|------|--------|------|------------|
| 用户登录/多账号 | P1 | JWT 鉴权 | 3 天 |
| 知识库共享 | P2 | 团队/班级共享 | 5 天 |
| OCR 图片识别 | P2 | 提取图片文字 | 2 天 |
| 语音输入 | P2 | Web Speech API | 3 天 |
| 模型管理后台 | P2 | 动态配置模型列表 | 2 天 |
| 导出对话 | P3 | PDF/Markdown | 2 天 |
| 移动端适配 | P3 | 响应式布局 | 5 天 |

---

## 七、附录

### 7.1 错误码

| 错误码 | 说明 | HTTP 状态 |
|--------|------|-----------|
| 400 | 请求参数错误 | 400 |
| 404 | 资源不存在 | 404 |
| 500 | 服务器内部错误 | 500 |

### 7.2 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DEEPSEEK_API_KEY | DeepSeek API 密钥 | - |
| DEEPSEEK_BASE_URL | API 地址 | https://api.deepseek.com |
| DEEPSEEK_MODEL | 默认模型 | deepseek-chat |
| DATABASE_URL | 数据库连接 | sqlite+aiosqlite:///./qa_agent.db |
| CORS_ORIGINS | 允许的来源 | http://localhost:5173 |

---

**文档结束**


# 新知识库 API 对接说明

## 已完成的工作

### 1. 创建 RAG 知识库服务 (`ragKnowledgeService.ts`)
- 对接 fifedu.com 的 RAG API
- 自动从浏览器 cookie 获取 token（支持 `token` 或 `Authorization` 字段）
- 实现的接口：
  - 获取个人知识库列表
  - 创建知识库
  - 删除知识库
  - 批量上传资源

### 2. 创建适配器 (`knowledgeAdapter.ts`)
- 将新 API 的数据格式适配到现有前端接口
- 保持组件代码不变，只修改底层服务
- 数据转换：
  - `RAGKnowledgeBase` → `KnowledgeBase`
  - 知识库 ID 从 number 转为 string
  - 资源数量映射为文档数量

### 3. 更新前端引用
- ✅ `KnowledgeBase.vue` - 使用新适配器
- ✅ `knowledge.ts` store - 使用新适配器

## Token 获取机制

系统会自动从 fifedu.com 的 cookie 中读取 token：

```typescript
function getToken(): string {
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'token' || name === 'Authorization') {
      return value
    }
  }
  return ''
}
```

**要求**：前端页面需要与 fifedu.com 在同一域名下，或者 fifedu.com 设置了跨域 cookie。

## API 端点

**Base URL**: `https://fifedu.com/rag/api/v1`

### 已对接接口

1. **获取知识库列表**
   - `GET /knowledge-base/get`
   - 支持分页、名称搜索、标签筛选

2. **创建知识库**
   - `POST /knowledge-base/create`
   - 必填：name, embeddingMode, type
   - 默认：embeddingMode='1' (qwen-embedding-v4), type=1 (个人知识库)

3. **删除知识库**
   - `DELETE /knowledge-base/delete/{id}`

4. **批量上传资源**
   - `POST /resource/batch-upload`
   - 需要先获取 resourceId（资源中心）

## 待完善功能

### ⚠️ 文件上传流程

新 API 的文件上传需要两步：
1. **先上传到资源中心** 获取 `resourceId`
2. **调用批量上传接口** 将资源添加到知识库

**当前状态**：
- `uploadDocument` 方法返回模拟数据
- 需要对接资源中心的文件上传接口

**解决方案**：
需要在 API 文档中找到资源中心的上传接口，类似：
```
POST /resource-center/upload
```

### 📋 其他待实现接口

1. **更新知识库** - 需要找到对应的 API
2. **获取文档列表** - 需要资源查询接口
3. **文档分块查询** - 需要对应的 API
4. **知识库搜索** - 需要对应的检索 API

## 测试步骤

### 1. 确保 Token 可用
```javascript
// 在浏览器控制台测试
document.cookie.split(';').find(c => c.includes('token'))
```

### 2. 测试知识库列表
访问前端页面，应该能看到从新 API 获取的知识库列表

### 3. 测试创建知识库
点击"创建知识库"按钮，填写信息后提交

### 4. 测试删除知识库
点击知识库卡片的删除按钮

## 注意事项

1. **跨域问题**：如果前端不在 fifedu.com 域名下，需要配置 CORS 或使用代理
2. **Token 格式**：当前使用 `Bearer {token}` 格式，如果 API 要求不同格式需要修改
3. **文件上传**：当前文件上传功能不完整，需要补充资源中心接口
4. **错误处理**：建议添加统一的错误处理和提示

## 下一步工作

1. 查找并对接资源中心的文件上传接口
2. 实现完整的文件上传流程
3. 对接资源列表查询接口
4. 对接知识库检索接口
5. 添加错误处理和加载状态
6. 测试所有功能

## 文件清单

- `/frontend/src/services/ragKnowledgeService.ts` - 新 API 服务
- `/frontend/src/services/knowledgeAdapter.ts` - 适配器
- `/frontend/src/stores/knowledge.ts` - 已更新
- `/frontend/src/components/knowledge/KnowledgeBase.vue` - 已更新

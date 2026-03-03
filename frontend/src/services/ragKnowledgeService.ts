// RAG 知识库服务 - 对接新的知识库 API
const BASE = '/rag/api/v1'

// 从 fifedu.com 获取 token
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

const req = (url: string, opts?: RequestInit) => {
  const token = getToken()
  return fetch(url, {
    ...opts,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
      ...opts?.headers,
    }
  }).then(r => r.json())
}

export interface RAGKnowledgeBase {
  id: number
  name: string
  labelId?: string
  labelName?: string
  description?: string
  icon?: string
  publicy: number
  resourceCount: number
  resourceTotalSize: number
  type?: number
  createTime: string
  updateTime: string
}

export interface RAGResource {
  id: number
  resourceId: string
  name: string
  fileSuffix: string
  fileSize: number
  buildStatus: number
  createTime: string
}

export const ragKnowledgeService = {
  // 获取个人知识库
  listBases: (params?: {
    name?: string
    labelId?: string
    pageIndex?: number
    pageSize?: number
  }): Promise<{ data: RAGKnowledgeBase[]; totalCount: number }> => {
    const query = new URLSearchParams(params as any).toString()
    return req(`${BASE}/knowledge-base/get${query ? '?' + query : ''}`)
  },

  // 创建知识库
  createBase: (data: {
    name: string
    embeddingMode: string
    type: number
    description?: string
    labelId?: string
    tagIds?: number[]
  }): Promise<RAGKnowledgeBase> =>
    req(`${BASE}/knowledge-base/create`, {
      method: 'POST',
      body: JSON.stringify({ id: 0, ...data })
    }),

  // 删除知识库
  deleteBase: (id: number): Promise<any> =>
    req(`${BASE}/knowledge-base/delete/${id}`, { method: 'DELETE' }),

  // 批量上传资源
  uploadResources: (data: {
    knowledgeBaseId: number
    resourceFiles: Array<{
      resourceId: string
      name: string
      fileSuffix: string
      fileSize: number
    }>
    splitMode?: number
    chunkSize?: number
    overlap?: number
  }): Promise<RAGResource[]> =>
    req(`${BASE}/resource/batch-upload`, {
      method: 'POST',
      body: JSON.stringify(data)
    }),
}

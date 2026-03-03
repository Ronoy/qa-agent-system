// 知识库服务适配器 - 将新 RAG API 适配到现有接口
import { ragKnowledgeService, type RAGKnowledgeBase } from './ragKnowledgeService'

// 适配后的接口类型（保持与现有代码兼容）
export interface KBTag { category: string; value: string }
export interface KnowledgeBase {
  id: string
  name: string
  description: string
  tags: KBTag[]
  created_at: string
  doc_count: number
}

export interface KBDocument {
  id: string
  file_name: string
  file_type: string
  status: string
  chunk_count: number
  created_at: string
}

// 将 RAG API 的知识库数据转换为前端格式
function adaptKnowledgeBase(rag: RAGKnowledgeBase): KnowledgeBase {
  return {
    id: String(rag.id),
    name: rag.name,
    description: rag.description || '',
    tags: rag.labelName ? [{ category: '标签', value: rag.labelName }] : [],
    created_at: rag.createTime,
    doc_count: rag.resourceCount
  }
}

export const knowledgeService = {
  // 获取标签分类（新 API 暂不支持，返回空）
  getTagCategories: (): Promise<Record<string, string[]>> =>
    Promise.resolve({}),

  // 获取知识库列表
  listBases: async (): Promise<KnowledgeBase[]> => {
    const res = await ragKnowledgeService.listBases({ pageSize: 100 })
    return res.data.map(adaptKnowledgeBase)
  },

  // 创建知识库
  createBase: async (data: { name: string; description: string; tags: KBTag[] }) => {
    const rag = await ragKnowledgeService.createBase({
      name: data.name,
      description: data.description,
      embeddingMode: '1', // 默认使用 qwen-embedding-v4
      type: 1 // 个人知识库
    })
    return adaptKnowledgeBase(rag)
  },

  // 更新知识库（新 API 需要单独实现，暂时返回成功）
  updateBase: (_id: string, _data: any) => Promise.resolve({ ok: true }),

  // 删除知识库
  deleteBase: (id: string) => ragKnowledgeService.deleteBase(Number(id)),

  // 获取文档列表（需要额外的资源查询接口，暂时返回空）
  listDocuments: (_kbId: string): Promise<KBDocument[]> => Promise.resolve([]),

  // 上传文档（简化实现，实际需要先上传到资源中心）
  uploadDocument: async (_kbId: string, file: File) => {
    // TODO: 实际需要先调用资源中心上传接口获取 resourceId
    // 这里暂时返回模拟数据
    console.warn('文件上传需要先对接资源中心接口')
    return {
      id: Date.now().toString(),
      file_name: file.name,
      file_type: file.name.split('.').pop() || '',
      status: 'pending'
    }
  },

  // 删除文档
  deleteDocument: (_kbId: string, _docId: string) => Promise.resolve({ ok: true }),

  // 获取文档分块
  getChunks: (_docId: string) => Promise.resolve([]),

  // 预览 URL
  previewUrl: (_docId: string) => '',

  // 预览 Excel
  previewExcel: (_docId: string) => Promise.resolve({ content: '' }),

  // 搜索
  search: (_kbId: string, _query: string, _top_k = 5) => Promise.resolve([])
}

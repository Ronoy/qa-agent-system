const BASE = 'http://localhost:8000/api/knowledge'

export interface KBTag { category: string; value: string }
export interface KnowledgeBase {
  id: string; name: string; description: string
  tags: KBTag[]; created_at: string; doc_count: number
}
export interface KBDocument {
  id: string; file_name: string; file_type: string
  status: string; chunk_count: number; created_at: string
}

const req = (url: string, opts?: RequestInit) =>
  fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts }).then(r => r.json())

export const knowledgeService = {
  getTagCategories: (): Promise<Record<string, string[]>> => req(`${BASE}/tag-categories`),
  listBases: (): Promise<KnowledgeBase[]> => req(`${BASE}/bases`),
  createBase: (data: { name: string; description: string; tags: KBTag[] }) =>
    req(`${BASE}/bases`, { method: 'POST', body: JSON.stringify(data) }),
  updateBase: (id: string, data: { name: string; description: string; tags: KBTag[] }) =>
    req(`${BASE}/bases/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteBase: (id: string) => req(`${BASE}/bases/${id}`, { method: 'DELETE' }),

  listDocuments: (kbId: string): Promise<KBDocument[]> => req(`${BASE}/bases/${kbId}/documents`),
  uploadDocument: (kbId: string, file: File) => {
    const fd = new FormData(); fd.append('file', file)
    return fetch(`${BASE}/bases/${kbId}/upload`, { method: 'POST', body: fd }).then(r => r.json())
  },
  deleteDocument: (kbId: string, docId: string) =>
    req(`${BASE}/bases/${kbId}/documents/${docId}`, { method: 'DELETE' }),
  getChunks: (docId: string): Promise<{ id: string; index: number; content: string; word_count: number }[]> =>
    req(`${BASE}/documents/${docId}/chunks`),
  previewUrl: (docId: string) => `${BASE}/documents/${docId}/preview`,
  previewExcel: (docId: string): Promise<{ content: string }> =>
    req(`${BASE}/documents/${docId}/preview`),
  search: (kbId: string, query: string, top_k = 5) =>
    req(`${BASE}/bases/${kbId}/search`, { method: 'POST', body: JSON.stringify({ query, top_k }) }),
}

<template>
  <div class="kb-page">

    <!-- ① 知识库列表 -->
    <template v-if="view === 'bases'">
      <div class="kb-header">
        <div class="header-left">
          <h2 class="page-title">个人知识库</h2>
          <span class="kb-count">{{ bases.length }} 个</span>
        </div>
        <button class="btn-primary" @click="openCreateModal">
          <svg viewBox="0 0 24 24" fill="none" width="13" height="13"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>
          创建知识库
        </button>
      </div>
      <div class="tag-bar">
        <span class="tag-pill" :class="{ active: !activeFilter }" @click="activeFilter=''">全部</span>
        <template v-for="(vals, cat) in tagCategories" :key="cat">
          <span v-for="v in vals" :key="v" class="tag-pill" :class="{ active: activeFilter===cat+':'+v }" @click="toggleFilter(cat,v)">{{ v }}</span>
        </template>
      </div>
      <div class="kb-grid">
        <div v-for="(kb, i) in filteredBases" :key="kb.id" class="kb-card" @click="enterKb(kb.id)">
          <div class="card-cover" :style="{ background: covers[i % covers.length] }"><div class="cover-blob"></div></div>
          <div class="card-body">
            <div class="card-title">{{ kb.name }}</div>
            <div class="card-desc">{{ kb.description || '暂无描述' }}</div>
            <div class="card-footer">
              <span class="card-meta">{{ kb.doc_count }} 个文档</span>
              <span v-for="t in kb.tags.slice(0,2)" :key="t.value" class="card-tag">{{ t.value }}</span>
            </div>
          </div>
          <button class="card-del" @click.stop="deleteBase(kb.id)">
            <svg viewBox="0 0 24 24" fill="none" width="12" height="12"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </button>
        </div>
        <div v-if="!filteredBases.length" class="kb-empty">
          <svg viewBox="0 0 24 24" fill="none" width="36" height="36"><path d="M4 19.5A2.5 2.5 0 016.5 17H20" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" stroke="currentColor" stroke-width="1.5"/></svg>
          <p>暂无知识库，点击右上角创建</p>
        </div>
      </div>
    </template>

    <!-- ② 文档列表 -->
    <template v-else-if="view === 'documents'">
      <div class="kb-header">
        <div class="header-left">
          <button class="btn-back" @click="view='bases'">
            <svg viewBox="0 0 24 24" fill="none" width="15" height="15"><path d="M19 12H5M12 5l-7 7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
          <h2 class="page-title">{{ selectedBase?.name }}</h2>
          <span class="kb-count">{{ documents.length }} 个文档</span>
        </div>
        <label class="btn-primary">
          <svg viewBox="0 0 24 24" fill="none" width="13" height="13"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          上传文件
          <input type="file" accept=".pdf,.jpg,.jpeg,.png,.webp,.xlsx,.xls" multiple hidden @change="handleUpload" />
        </label>
      </div>
      <div class="doc-grid">
        <div v-for="doc in documents" :key="doc.id" class="doc-card"
          @click="doc.status==='done' ? enterChunks(doc) : openPreview(doc)">
          <div class="doc-icon-wrap" :class="doc.file_type">
            <svg v-if="doc.file_type==='pdf'" viewBox="0 0 24 24" fill="none" width="26" height="26"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="currentColor" stroke-width="1.8"/><path d="M14 2v6h6M9 13h6M9 17h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
            <svg v-else-if="doc.file_type==='image'" viewBox="0 0 24 24" fill="none" width="26" height="26"><rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="1.8"/><circle cx="8.5" cy="8.5" r="1.5" stroke="currentColor" stroke-width="1.8"/><path d="M21 15l-5-5L5 21" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
            <svg v-else viewBox="0 0 24 24" fill="none" width="26" height="26"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="currentColor" stroke-width="1.8"/><path d="M8 13h8M8 17h5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
          </div>
          <div class="doc-info">
            <div class="doc-name" :title="doc.file_name">{{ doc.file_name }}</div>
            <div class="doc-status" :class="doc.status">{{ statusLabel[doc.status] }}<span v-if="doc.status==='done'"> · {{ doc.chunk_count }} 块</span></div>
          </div>
          <button class="card-del" @click.stop="deleteDoc(doc.id)">
            <svg viewBox="0 0 24 24" fill="none" width="12" height="12"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </button>
        </div>
        <div v-if="!documents.length" class="kb-empty"><p>上传 PDF、图片或 Excel 开始构建知识库</p></div>
      </div>
    </template>

    <!-- ③ 知识块预览 -->
    <template v-else-if="view === 'chunks'">
      <div class="kb-header">
        <div class="header-left">
          <button class="btn-back" @click="view='documents'">
            <svg viewBox="0 0 24 24" fill="none" width="15" height="15"><path d="M19 12H5M12 5l-7 7 7 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
          <h2 class="page-title">{{ currentDoc?.file_name }}</h2>
          <span class="kb-count">{{ chunks.length }} 个知识块</span>
        </div>
      </div>
      <div class="chunk-viewer">
        <div class="chunk-nav">
          <div v-for="c in chunks" :key="c.id" class="chunk-nav-item"
            :class="{ active: activeChunkId === c.id }" @click="activeChunkId = c.id">
            <span class="chunk-nav-index"># {{ c.index + 1 }}</span>
            <span class="chunk-nav-words">{{ c.word_count }} 字</span>
          </div>
        </div>
        <div class="chunk-content">
          <template v-if="activeChunk">
            <div class="chunk-content-header">
              <span>块 #{{ activeChunk.index + 1 }}</span>
              <span class="chunk-words-badge">{{ activeChunk.word_count }} 字</span>
            </div>
            <div class="chunk-text">{{ activeChunk.content }}</div>
          </template>
          <div v-else class="kb-empty"><p>选择左侧知识块查看内容</p></div>
        </div>
      </div>
    </template>

    <!-- 新建弹窗 -->
    <div v-if="showModal" class="modal-mask" @click.self="showModal=false">
      <div class="modal">
        <div class="modal-title">新建知识库</div>
        <input v-model="form.name" class="modal-input" placeholder="知识库名称" />
        <textarea v-model="form.description" class="modal-input" placeholder="描述（可选）" rows="2" />
        <div v-for="(vals, cat) in tagCategories" :key="cat" class="modal-tag-row">
          <span class="modal-cat">{{ cat }}</span>
          <div class="tag-chips">
            <span v-for="v in vals" :key="v" class="tag-pill" :class="{ active: isTagSelected(cat,v) }" @click="toggleFormTag(cat,v)">{{ v }}</span>
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showModal=false">取消</button>
          <button class="btn-primary" @click="submitCreate">创建</button>
        </div>
      </div>
    </div>

    <!-- 文件预览弹窗 -->
    <div v-if="previewDoc" class="modal-mask" @click.self="previewDoc=null">
      <div class="modal modal-preview">
        <div class="modal-title">{{ previewDoc.file_name }}</div>
        <div class="preview-body">
          <iframe v-if="previewDoc.file_type==='pdf'" :src="previewUrl" class="preview-iframe" />
          <img v-else-if="previewDoc.file_type==='image'" :src="previewUrl" class="preview-img" />
          <pre v-else class="preview-text">{{ excelContent }}</pre>
        </div>
        <button class="btn-cancel" style="margin-top:12px" @click="previewDoc=null">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useKnowledgeStore } from '@/stores/knowledge'
import { knowledgeService, type KBDocument } from '@/services/knowledgeAdapter'

const store = useKnowledgeStore()
const { bases, documents, selectedKbId, tagCategories } = storeToRefs(store)

const view = ref<'bases' | 'documents' | 'chunks'>('bases')
const activeFilter = ref('')
const showModal = ref(false)
const form = ref({ name: '', description: '', tags: [] as { category: string; value: string }[] })
const previewDoc = ref<KBDocument | null>(null)
const previewUrl = ref('')
const excelContent = ref('')
const currentDoc = ref<KBDocument | null>(null)
const chunks = ref<{ id: string; index: number; content: string; word_count: number }[]>([])
const activeChunkId = ref<string | null>(null)

const covers = [
  'linear-gradient(135deg,#667eea,#764ba2)',
  'linear-gradient(135deg,#f093fb,#f5576c)',
  'linear-gradient(135deg,#4facfe,#00f2fe)',
  'linear-gradient(135deg,#43e97b,#38f9d7)',
  'linear-gradient(135deg,#fa709a,#fee140)',
  'linear-gradient(135deg,#a18cd1,#fbc2eb)',
  'linear-gradient(135deg,#fccb90,#d57eeb)',
  'linear-gradient(135deg,#a1c4fd,#c2e9fb)',
]
const statusLabel: Record<string, string> = { pending: '等待处理', processing: '处理中...', done: '已完成', error: '处理失败' }

const selectedBase = computed(() => bases.value.find(b => b.id === selectedKbId.value))
const activeChunk = computed(() => chunks.value.find(c => c.id === activeChunkId.value))
const filteredBases = computed(() => {
  if (!activeFilter.value) return bases.value
  const [cat, val] = activeFilter.value.split(':')
  return bases.value.filter(kb => kb.tags.some(t => t.category === cat && t.value === val))
})

function toggleFilter(cat: string, val: string) {
  const key = cat + ':' + val
  activeFilter.value = activeFilter.value === key ? '' : key
}
async function enterKb(id: string) {
  await store.fetchDocuments(id)
  view.value = 'documents'
}
async function enterChunks(doc: KBDocument) {
  currentDoc.value = doc
  chunks.value = await knowledgeService.getChunks(doc.id)
  activeChunkId.value = chunks.value[0]?.id ?? null
  view.value = 'chunks'
}
function openCreateModal() { form.value = { name: '', description: '', tags: [] }; showModal.value = true }
function isTagSelected(cat: string, val: string) { return form.value.tags.some(t => t.category === cat && t.value === val) }
function toggleFormTag(cat: string, val: string) {
  const idx = form.value.tags.findIndex(t => t.category === cat && t.value === val)
  if (idx >= 0) form.value.tags.splice(idx, 1)
  else form.value.tags.push({ category: cat, value: val })
}
async function submitCreate() {
  if (!form.value.name.trim()) return
  await knowledgeService.createBase(form.value)
  showModal.value = false
  await store.fetchBases()
}
async function deleteBase(id: string) {
  if (!confirm('确认删除该知识库？')) return
  await knowledgeService.deleteBase(id)
  await store.fetchBases()
}
async function handleUpload(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files || !selectedKbId.value) return
  for (const file of Array.from(files)) await knowledgeService.uploadDocument(selectedKbId.value, file)
  await store.fetchDocuments(selectedKbId.value)
  const timer = setInterval(async () => {
    await store.fetchDocuments(selectedKbId.value!)
    if (!documents.value.some(d => d.status === 'pending' || d.status === 'processing')) clearInterval(timer)
  }, 2000)
}
async function deleteDoc(docId: string) {
  if (!selectedKbId.value) return
  await knowledgeService.deleteDocument(selectedKbId.value, docId)
  await store.fetchDocuments(selectedKbId.value)
}
async function openPreview(doc: KBDocument) {
  previewDoc.value = doc; excelContent.value = ''
  if (doc.file_type === 'excel') { excelContent.value = (await knowledgeService.previewExcel(doc.id)).content }
  else { previewUrl.value = knowledgeService.previewUrl(doc.id) }
}
onMounted(async () => { await store.fetchTagCategories(); await store.fetchBases() })
</script>

<style scoped>
.kb-page { flex: 1; display: flex; flex-direction: column; height: 100%; overflow: hidden; background: #f7f8fa; }

.kb-header { display: flex; align-items: center; justify-content: space-between; padding: 24px 32px 16px; flex-shrink: 0; background: #fff; border-bottom: 1px solid #e5e7eb; }
.header-left { display: flex; align-items: center; gap: 10px; }
.page-title { font-size: 18px; font-weight: 700; color: #111827; }
.kb-count { font-size: 12px; color: #9ca3af; background: #f3f4f6; padding: 2px 8px; border-radius: 99px; }
.btn-primary { display: flex; align-items: center; gap: 6px; padding: 8px 16px; background: #6366f1; color: #fff; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 500; transition: background 0.15s; }
.btn-primary:hover { background: #4f46e5; }
.btn-back { width: 30px; height: 30px; border-radius: 7px; border: 1px solid #e5e7eb; background: #fff; color: #6b7280; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.btn-back:hover { border-color: #6366f1; color: #6366f1; }

.tag-bar { display: flex; flex-wrap: wrap; gap: 6px; padding: 12px 32px; background: #fff; border-bottom: 1px solid #f3f4f6; flex-shrink: 0; }
.tag-pill { font-size: 12px; padding: 4px 12px; border-radius: 99px; background: #f3f4f6; color: #6b7280; cursor: pointer; border: 1px solid transparent; transition: all 0.15s; }
.tag-pill:hover { border-color: #6366f1; color: #6366f1; }
.tag-pill.active { background: #eef2ff; color: #6366f1; border-color: #6366f1; }

.kb-grid { flex: 1; overflow-y: auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 18px; padding: 24px 32px; align-content: start; }
.kb-card { background: #fff; border-radius: 14px; overflow: hidden; cursor: pointer; position: relative; border: 1px solid #e5e7eb; transition: all 0.2s; }
.kb-card:hover { border-color: #a5b4fc; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(99,102,241,0.1); }
.card-cover { height: 120px; position: relative; overflow: hidden; }
.cover-blob { position: absolute; width: 100px; height: 100px; border-radius: 50%; background: rgba(255,255,255,0.2); top: -20px; right: -10px; filter: blur(24px); }
.card-body { padding: 14px 16px; }
.card-title { font-size: 14px; font-weight: 600; color: #111827; margin-bottom: 4px; }
.card-desc { font-size: 12px; color: #9ca3af; margin-bottom: 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-footer { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.card-meta { font-size: 11px; color: #9ca3af; }
.card-tag { font-size: 11px; padding: 1px 7px; border-radius: 99px; background: #eef2ff; color: #6366f1; }
.card-del { position: absolute; top: 8px; right: 8px; opacity: 0; width: 24px; height: 24px; border-radius: 6px; border: none; background: rgba(255,255,255,0.9); color: #9ca3af; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.kb-card:hover .card-del { opacity: 1; }
.card-del:hover { background: #fee2e2; color: #ef4444; }

.doc-grid { flex: 1; overflow-y: auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 16px; padding: 24px 32px; align-content: start; }
.doc-card { background: #fff; border-radius: 12px; padding: 20px 16px; cursor: pointer; position: relative; border: 1px solid #e5e7eb; transition: all 0.2s; display: flex; flex-direction: column; align-items: center; gap: 12px; }
.doc-card:hover { border-color: #a5b4fc; transform: translateY(-2px); box-shadow: 0 4px 16px rgba(99,102,241,0.08); }
.doc-icon-wrap { width: 52px; height: 52px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.doc-icon-wrap.pdf { background: #fee2e2; color: #ef4444; }
.doc-icon-wrap.image { background: #dbeafe; color: #3b82f6; }
.doc-icon-wrap.excel { background: #dcfce7; color: #22c55e; }
.doc-info { text-align: center; width: 100%; }
.doc-name { font-size: 12px; font-weight: 500; color: #111827; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.doc-status { font-size: 11px; margin-top: 3px; color: #9ca3af; }
.doc-status.done { color: #22c55e; }
.doc-status.error { color: #ef4444; }
.doc-status.processing { color: #f59e0b; }

.kb-empty { grid-column: 1/-1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; padding: 60px 0; color: #9ca3af; }
.kb-empty p { font-size: 13px; }

/* 知识块预览 */
.chunk-viewer { flex: 1; display: flex; overflow: hidden; }
.chunk-nav { width: 220px; flex-shrink: 0; border-right: 1px solid #e5e7eb; overflow-y: auto; background: #fff; padding: 8px; }
.chunk-nav-item { display: flex; align-items: center; justify-content: space-between; padding: 9px 12px; border-radius: 8px; cursor: pointer; transition: background 0.12s; }
.chunk-nav-item:hover { background: #f3f4f6; }
.chunk-nav-item.active { background: #eef2ff; }
.chunk-nav-index { font-size: 13px; font-weight: 500; color: #374151; }
.chunk-nav-item.active .chunk-nav-index { color: #6366f1; }
.chunk-nav-words { font-size: 11px; color: #9ca3af; }
.chunk-content { flex: 1; overflow-y: auto; padding: 24px 32px; }
.chunk-content-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #e5e7eb; }
.chunk-content-header span { font-size: 15px; font-weight: 600; color: #111827; }
.chunk-words-badge { font-size: 12px; color: #6366f1; background: #eef2ff; padding: 2px 10px; border-radius: 99px; font-weight: 400; }
.chunk-text { font-size: 14px; line-height: 1.8; color: #374151; white-space: pre-wrap; word-break: break-word; }

/* Modal */
.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: #fff; border-radius: 16px; padding: 28px; width: 440px; max-height: 80vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
.modal-preview { width: 780px; }
.modal-title { font-size: 16px; font-weight: 600; color: #111827; margin-bottom: 16px; }
.modal-input { width: 100%; border: 1px solid #e5e7eb; border-radius: 8px; padding: 9px 12px; font-size: 13px; color: #111827; margin-bottom: 10px; outline: none; resize: vertical; font-family: inherit; background: #fff; }
.modal-input:focus { border-color: #6366f1; }
.modal-tag-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 10px; }
.modal-cat { font-size: 12px; color: #9ca3af; white-space: nowrap; padding-top: 5px; min-width: 32px; }
.tag-chips { display: flex; flex-wrap: wrap; gap: 5px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
.btn-cancel { padding: 7px 16px; border: 1px solid #e5e7eb; background: none; border-radius: 8px; cursor: pointer; font-size: 13px; color: #6b7280; }
.btn-cancel:hover { border-color: #9ca3af; }
.preview-body { width: 100%; height: 520px; overflow: auto; }
.preview-iframe { width: 100%; height: 100%; border: none; }
.preview-img { max-width: 100%; max-height: 100%; object-fit: contain; display: block; margin: auto; }
.preview-text { font-size: 12px; white-space: pre-wrap; word-break: break-all; color: #374151; }
</style>

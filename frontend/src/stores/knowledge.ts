import { defineStore } from 'pinia'
import { ref } from 'vue'
import { knowledgeService, type KnowledgeBase, type KBDocument } from '@/services/knowledgeAdapter'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const bases = ref<KnowledgeBase[]>([])
  const documents = ref<KBDocument[]>([])
  const selectedKbId = ref<string | null>(null)
  const tagCategories = ref<Record<string, string[]>>({})

  async function fetchBases() {
    bases.value = await knowledgeService.listBases()
  }
  async function fetchDocuments(kbId: string) {
    selectedKbId.value = kbId
    documents.value = await knowledgeService.listDocuments(kbId)
  }
  async function fetchTagCategories() {
    tagCategories.value = await knowledgeService.getTagCategories()
  }

  return { bases, documents, selectedKbId, tagCategories, fetchBases, fetchDocuments, fetchTagCategories }
})

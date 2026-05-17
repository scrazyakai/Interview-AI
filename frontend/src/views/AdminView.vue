<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { API_BASE_URL, loadAuthSession } from '../utils/auth'

// ── 统计 ────────────────────────────────────────────────────
const stats = ref({ total_users: 0, total_documents: 0, total_chunks: 0, indexed_documents: 0 })

// ── 文档列表 ─────────────────────────────────────────────────
interface DocItem {
  doc_id: number
  title: string
  file_name: string
  category: string
  status: string
  chunk_count: number
  created_at: string
}
const docs = ref<DocItem[]>([])
const docsTotal = ref(0)

// ── 上传表单 ─────────────────────────────────────────────────
const uploadTitle = ref('')
const uploadCategory = ref('general')
const uploadFile = ref<File | null>(null)
const uploading = ref(false)
const uploadMsg = ref('')
const uploadError = ref('')

const categories = [
  { value: 'general', label: '通用' },
  { value: 'frontend', label: '前端' },
  { value: 'backend', label: '后端' },
  { value: 'database', label: '数据库' },
  { value: 'algorithm', label: '算法' },
  { value: 'behavioral', label: '行为面试' },
]

function authHeaders() {
  const s = loadAuthSession()
  return s ? { Authorization: `${s.token_type} ${s.access_token}` } : {}
}

async function fetchStats() {
  try {
    const res = await fetch(`${API_BASE_URL}/admin/stats`, { headers: authHeaders() })
    const json = await res.json()
    if (!res.ok) {
      console.error('[admin] stats error:', json)
      return
    }
    if (json.data) stats.value = json.data
  } catch (e) {
    console.error('[admin] fetchStats failed:', e)
  }
}

async function fetchDocs() {
  const res = await fetch(`${API_BASE_URL}/admin/documents?page=1&page_size=20`, { headers: authHeaders() })
  const json = await res.json()
  if (json.data) {
    docs.value = json.data.items
    docsTotal.value = json.data.total
  }
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  uploadFile.value = input.files?.[0] ?? null
}

async function handleUpload() {
  if (!uploadTitle.value.trim()) { uploadError.value = '请填写文档标题'; return }
  if (!uploadFile.value) { uploadError.value = '请选择文件'; return }
  uploadError.value = ''
  uploading.value = true
  uploadMsg.value = ''
  try {
    const form = new FormData()
    form.append('title', uploadTitle.value.trim())
    form.append('category', uploadCategory.value)
    form.append('file', uploadFile.value)
    const res = await fetch(`${API_BASE_URL}/admin/documents/upload`, {
      method: 'POST',
      headers: authHeaders(),
      body: form,
    })
    const json = await res.json()
    if (!res.ok) throw new Error(json.message || '上传失败')
    uploadMsg.value = `上传成功，正在后台索引（doc_id: ${json.data?.doc_id}）`
    uploadTitle.value = ''
    uploadCategory.value = 'general'
    uploadFile.value = null
    ;(document.getElementById('file-input') as HTMLInputElement).value = ''
    await fetchDocs()
    await fetchStats()
  } catch (err: unknown) {
    uploadError.value = err instanceof Error ? err.message : '上传失败'
  } finally {
    uploading.value = false
  }
}

async function reindex(docId: number) {
  await fetch(`${API_BASE_URL}/admin/documents/${docId}/reindex`, {
    method: 'POST',
    headers: authHeaders(),
  })
  await fetchDocs()
}

async function deleteDoc(docId: number) {
  if (!confirm('确认删除该文档及其所有向量数据？')) return
  await fetch(`${API_BASE_URL}/admin/documents/${docId}`, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  await fetchDocs()
  await fetchStats()
}

const statusColor: Record<string, string> = {
  pending: '#f59e0b',
  indexed: '#10b981',
  failed: '#ef4444',
}

onMounted(() => {
  fetchStats()
  fetchDocs()
})
</script>

<template>
  <div style="min-height:100vh;background:#f4f6fb;padding-top:80px;">
    <div style="max-width:960px;margin:0 auto;padding:32px 20px;">

      <!-- 标题 -->
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:28px;">
        <svg viewBox="0 0 24 24" fill="#7c3aed" style="width:24px;height:24px;">
          <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-1 14H9V9h2v6zm4 0h-2V9h2v6z"/>
        </svg>
        <h1 style="margin:0;font-size:22px;font-weight:700;color:#1e1e2e;font-family:'Inter',sans-serif;">管理后台</h1>
      </div>

      <!-- 统计卡片 -->
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:32px;">
        <div v-for="(item, key) in [
          { label: '注册用户', value: stats.total_users },
          { label: '上传文档', value: stats.total_documents },
          { label: '已索引', value: stats.indexed_documents },
          { label: '向量块', value: stats.total_chunks },
        ]" :key="key"
          style="background:#fff;border-radius:12px;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,0.06);"
        >
          <div style="font-size:28px;font-weight:700;color:#1e1e2e;font-family:'Inter',sans-serif;">{{ item.value }}</div>
          <div style="font-size:13px;color:#6b7280;margin-top:4px;">{{ item.label }}</div>
        </div>
      </div>

      <!-- 上传文档 -->
      <div style="background:#fff;border-radius:16px;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,0.06);margin-bottom:28px;">
        <h2 style="margin:0 0 20px;font-size:16px;font-weight:700;color:#1e1e2e;font-family:'Inter',sans-serif;">上传文档</h2>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;">
          <div>
            <label style="display:block;font-size:13px;font-weight:600;color:#374151;margin-bottom:6px;">文档标题 *</label>
            <input
              v-model="uploadTitle"
              placeholder="例：Vue3 前端面试题库"
              style="width:100%;box-sizing:border-box;padding:9px 12px;border-radius:8px;border:1px solid #d1d5db;font-size:14px;outline:none;font-family:'Inter',sans-serif;"
            />
          </div>
          <div>
            <label style="display:block;font-size:13px;font-weight:600;color:#374151;margin-bottom:6px;">分类</label>
            <select
              v-model="uploadCategory"
              style="width:100%;box-sizing:border-box;padding:9px 12px;border-radius:8px;border:1px solid #d1d5db;font-size:14px;outline:none;font-family:'Inter',sans-serif;background:#fff;"
            >
              <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
            </select>
          </div>
        </div>

        <div style="margin-bottom:16px;">
          <label style="display:block;font-size:13px;font-weight:600;color:#374151;margin-bottom:6px;">文件（PDF / TXT / MD，最大 10MB）*</label>
          <input
            id="file-input"
            type="file"
            accept=".pdf,.txt,.md,text/plain,application/pdf"
            style="font-size:14px;font-family:'Inter',sans-serif;"
            @change="onFileChange"
          />
        </div>

        <div v-if="uploadError" style="color:#ef4444;font-size:13px;margin-bottom:10px;">{{ uploadError }}</div>
        <div v-if="uploadMsg" style="color:#10b981;font-size:13px;margin-bottom:10px;">{{ uploadMsg }}</div>

        <button
          type="button"
          :disabled="uploading"
          style="padding:10px 24px;border-radius:8px;background:#7c3aed;color:#fff;font-size:14px;font-weight:600;border:none;cursor:pointer;font-family:'Inter',sans-serif;opacity:1;transition:opacity 0.15s;"
          :style="{ opacity: uploading ? 0.6 : 1, cursor: uploading ? 'not-allowed' : 'pointer' }"
          @click="handleUpload"
        >
          {{ uploading ? '上传中…' : '上传并索引' }}
        </button>
      </div>

      <!-- 文档列表 -->
      <div style="background:#fff;border-radius:16px;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
        <h2 style="margin:0 0 20px;font-size:16px;font-weight:700;color:#1e1e2e;font-family:'Inter',sans-serif;">
          文档列表（共 {{ docsTotal }} 个）
        </h2>

        <div v-if="docs.length === 0" style="color:#9ca3af;font-size:14px;">暂无文档</div>

        <table v-else style="width:100%;border-collapse:collapse;font-size:14px;font-family:'Inter',sans-serif;">
          <thead>
            <tr style="border-bottom:2px solid #f3f4f6;">
              <th style="text-align:left;padding:8px 12px;color:#6b7280;font-weight:600;">标题</th>
              <th style="text-align:left;padding:8px 12px;color:#6b7280;font-weight:600;">分类</th>
              <th style="text-align:center;padding:8px 12px;color:#6b7280;font-weight:600;">状态</th>
              <th style="text-align:center;padding:8px 12px;color:#6b7280;font-weight:600;">Chunks</th>
              <th style="text-align:right;padding:8px 12px;color:#6b7280;font-weight:600;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="doc in docs"
              :key="doc.doc_id"
              style="border-bottom:1px solid #f3f4f6;"
            >
              <td style="padding:10px 12px;color:#1e1e2e;max-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                {{ doc.title }}
              </td>
              <td style="padding:10px 12px;color:#6b7280;">{{ doc.category }}</td>
              <td style="padding:10px 12px;text-align:center;">
                <span :style="{
                  display:'inline-block',
                  padding:'2px 10px',
                  borderRadius:'999px',
                  fontSize:'12px',
                  fontWeight:'600',
                  background: statusColor[doc.status] + '18',
                  color: statusColor[doc.status] || '#6b7280',
                }">{{ doc.status }}</span>
              </td>
              <td style="padding:10px 12px;text-align:center;color:#6b7280;">{{ doc.chunk_count }}</td>
              <td style="padding:10px 12px;text-align:right;">
                <button
                  type="button"
                  style="padding:4px 10px;border-radius:6px;border:1px solid #d1d5db;background:transparent;font-size:12px;cursor:pointer;color:#374151;margin-right:6px;"
                  @click="reindex(doc.doc_id)"
                >重建索引</button>
                <button
                  type="button"
                  style="padding:4px 10px;border-radius:6px;border:1px solid #fca5a5;background:transparent;font-size:12px;cursor:pointer;color:#ef4444;"
                  @click="deleteDoc(doc.doc_id)"
                >删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>

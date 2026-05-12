<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { RouterLink } from 'vue-router'

import {
  API_BASE_URL,
  clearAuthSession,
  extractApiPayload,
  getApiErrorMessage,
  loadAuthSession,
  type TokenResponse,
} from '../utils/auth'

type ProfileData = {
  username?: string
  user_id?: string
  avatar_url?: string | null
  total_points?: number
  [key: string]: unknown
}

type PointRecord = {
  item?: string
  change_point?: number
  description?: string | null
  amount?: number | string | null
  order_no?: string | null
  created_at?: string
  [key: string]: unknown
}

type PointRecordListResponse = {
  total?: number
  items?: PointRecord[]
}

type ProfileField = {
  key: string
  label: string
  value: string
}

type DisplayPointRecord = {
  item: string
  changePoint: number
  description: string
  amount: string
  orderNo: string
  createdAt: string
  sign: 'positive' | 'negative' | 'neutral'
}

const router = useRouter()
const PAGE_SIZE = 10

const session = ref<TokenResponse | null>(null)
const profileLoading = ref(true)
const profileError = ref('')
const profileData = ref<ProfileData | null>(null)
const pointRecords = ref<PointRecord[]>([])
const totalRecordCount = ref(0)
const currentPage = ref(1)

const resumeUploading = ref(false)
const resumeUploadError = ref('')
const resumeFileInput = ref<HTMLInputElement | null>(null)

// ── 通知系统 ─────────────────────────────────────────────────
type Toast = { id: number; type: 'info' | 'success' | 'error'; message: string }
const toasts = ref<Toast[]>([])
let toastSeq = 0
function addToast(type: Toast['type'], message: string, duration = 5000) {
  const id = ++toastSeq
  toasts.value.push({ id, type, message })
  setTimeout(() => { toasts.value = toasts.value.filter(t => t.id !== id) }, duration)
}
function removeToast(id: number) {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

// ── 简历解析轮询 ─────────────────────────────────────────────
let pollTimer: ReturnType<typeof setInterval> | null = null
function startPolling(resumeId: number) {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const list = await requestWithAuth<ResumeListItem[]>('/resume/list')
      const target = list.find(r => r.id === resumeId)
      if (!target) return
      if (target.parse_status === 'success') {
        clearInterval(pollTimer!)
        pollTimer = null
        resumeList.value = list
        resumeUploading.value = false
        addToast('success', `「${target.file_name}」解析完成 ✓`)
      } else if (target.parse_status === 'failed') {
        clearInterval(pollTimer!)
        pollTimer = null
        resumeList.value = list
        resumeUploading.value = false
        addToast('error', `「${target.file_name}」解析失败，请重新上传`)
      }
    } catch { /* 静默失败，继续轮询 */ }
  }, 3000)
}

type ResumeListItem = {
  id: number
  resume_uuid: string
  file_name: string
  parse_status: string
  name?: string | null
  created_at: string
}

type ResumeParseResult = {
  name?: string | null
  email?: string | null
  phone?: string | null
  location?: string | null
  summary?: string | null
  skills?: string[]
  total_years_exp?: number | null
  work_experiences?: { id?: number; company: string; title?: string | null; start_date?: string | null; end_date?: string | null; description?: string | null; tech_stack?: string[] }[]
  projects?: { id?: number; name: string; role?: string | null; start_date?: string | null; end_date?: string | null; description?: string | null; tech_stack?: string[] }[]
  educations?: { id?: number; school: string; degree?: string | null; major?: string | null; graduation_year?: string | null }[]
}

// modal 状态
const resumeModalOpen = ref(false)
const resumeModalLoading = ref(false)
const resumeModalError = ref('')
// 列表视图
const resumeList = ref<ResumeListItem[]>([])
// 详情视图
const resumeDetail = ref<ResumeParseResult | null>(null)
const resumeDetailId = ref<number | null>(null)
// 删除中
const deletingId = ref<number | null>(null)
const isEditing = ref(false)
const isSaving = ref(false)
type EditForm = { name: string; email: string; phone: string; location: string; summary: string; total_years_exp: string }
const editForm = ref<EditForm>({ name: '', email: '', phone: '', location: '', summary: '', total_years_exp: '' })
const editSkills = ref<string[]>([])
const newSkillInput = ref('')

// 通用确认弹窗
const confirmDialog = ref<{ open: boolean; title: string; message: string; resolve: ((v: boolean) => void) | null }>({
  open: false, title: '', message: '', resolve: null,
})
function showConfirm(title: string, message: string): Promise<boolean> {
  return new Promise(resolve => {
    confirmDialog.value = { open: true, title, message, resolve }
  })
}
function onConfirmOk() {
  confirmDialog.value.resolve?.(true)
  confirmDialog.value.open = false
}
function onConfirmCancel() {
  confirmDialog.value.resolve?.(false)
  confirmDialog.value.open = false
}

// 工作经历内联编辑
type WorkExpForm = { company: string; title: string; start_date: string; end_date: string; description: string; tech_stack: string }
const editingWorkExpId = ref<number | 'new' | null>(null)
const workExpForm = ref<WorkExpForm>({ company: '', title: '', start_date: '', end_date: '', description: '', tech_stack: '' })
const savingWorkExp = ref(false)

// 教育经历内联编辑
type EduForm = { school: string; degree: string; major: string; graduation_year: string }
const editingEduId = ref<number | 'new' | null>(null)
const eduForm = ref<EduForm>({ school: '', degree: '', major: '', graduation_year: '' })
const savingEdu = ref(false)

// 项目经历内联编辑
type ProjectForm = { name: string; role: string; start_date: string; end_date: string; description: string; tech_stack: string }
const editingProjectId = ref<number | 'new' | null>(null)
const projectForm = ref<ProjectForm>({ name: '', role: '', start_date: '', end_date: '', description: '', tech_stack: '' })
const savingProject = ref(false)

function closeResumeModal() {
  resumeModalOpen.value = false
  resumeDetail.value = null
  resumeDetailId.value = null
}

async function openResumeModal() {
  resumeModalOpen.value = true
  resumeDetail.value = null
  resumeDetailId.value = null
  resumeModalLoading.value = true
  resumeModalError.value = ''
  try {
    resumeList.value = await requestWithAuth<ResumeListItem[]>('/resume/list')
  } catch (error) {
    resumeModalError.value = error instanceof Error ? error.message : '获取简历列表失败'
  } finally {
    resumeModalLoading.value = false
  }
}

async function openResumeDetail(id: number) {
  resumeDetailId.value = id
  resumeModalLoading.value = true
  resumeModalError.value = ''
  try {
    resumeDetail.value = await requestWithAuth<ResumeParseResult>(`/resume/result/${id}`)
  } catch (error) {
    resumeModalError.value = error instanceof Error ? error.message : '获取解析详情失败'
  } finally {
    resumeModalLoading.value = false
  }
}

function backToList() {
  resumeDetail.value = null
  resumeDetailId.value = null
  resumeModalError.value = ''
  isEditing.value = false
}

function startEditing() {
  const d = resumeDetail.value!
  editForm.value = {
    name: d.name ?? '',
    email: d.email ?? '',
    phone: d.phone ?? '',
    location: d.location ?? '',
    summary: d.summary ?? '',
    total_years_exp: d.total_years_exp != null ? String(d.total_years_exp) : '',
  }
  editSkills.value = [...(d.skills ?? [])]
  newSkillInput.value = ''
  isEditing.value = true
}

function addSkill() {
  const s = newSkillInput.value.trim()
  if (s && !editSkills.value.includes(s)) {
    editSkills.value.push(s)
  }
  newSkillInput.value = ''
}

function removeSkill(index: number) {
  editSkills.value.splice(index, 1)
}

async function saveEdit() {
  if (!resumeDetailId.value) return
  isSaving.value = true
  resumeModalError.value = ''
  try {
    const payload: Record<string, unknown> = {
      skills: editSkills.value,
    }
    if (editForm.value.name) payload.name = editForm.value.name
    if (editForm.value.email) payload.email = editForm.value.email
    if (editForm.value.phone) payload.phone = editForm.value.phone
    if (editForm.value.location) payload.location = editForm.value.location
    if (editForm.value.summary) payload.summary = editForm.value.summary
    if (editForm.value.total_years_exp !== '') payload.total_years_exp = Number(editForm.value.total_years_exp)
    await postWithAuth(`/resume/${resumeDetailId.value}/update`, payload)
    // 更新本地详情数据
    Object.assign(resumeDetail.value!, {
      name: editForm.value.name || null,
      email: editForm.value.email || null,
      phone: editForm.value.phone || null,
      location: editForm.value.location || null,
      summary: editForm.value.summary || null,
      total_years_exp: editForm.value.total_years_exp !== '' ? Number(editForm.value.total_years_exp) : null,
      skills: [...editSkills.value],
    })
    // 同步列表里的姓名
    const listItem = resumeList.value.find(r => r.id === resumeDetailId.value)
    if (listItem) listItem.name = editForm.value.name || null
    isEditing.value = false
  } catch (error) {
    resumeModalError.value = error instanceof Error ? error.message : '保存失败'
  } finally {
    isSaving.value = false
  }
}

async function deleteResume(id: number) {
  if (!await showConfirm('删除简历', '确认删除这份简历？此操作不可恢复。')) return
  deletingId.value = id
  try {
    await postWithAuth(`/resume/${id}/delete`)
    resumeList.value = resumeList.value.filter(r => r.id !== id)
    if (resumeDetailId.value === id) backToList()
  } catch (error) {
    resumeModalError.value = error instanceof Error ? error.message : '删除失败'
  } finally {
    deletingId.value = null
  }
}

// ── 工作经历操作 ────────────────────────────────────────────
function startEditWorkExp(w: { id?: number; company: string; title?: string | null; start_date?: string | null; end_date?: string | null; description?: string | null; tech_stack?: string[] }) {
  if (w.id == null) {
    resumeModalError.value = '工作经历 ID 缺失，请关闭后重新打开详情页再编辑'
    return
  }
  editingWorkExpId.value = w.id
  workExpForm.value = {
    company: w.company,
    title: w.title ?? '',
    start_date: w.start_date ?? '',
    end_date: w.end_date ?? '',
    description: w.description ?? '',
    tech_stack: (w.tech_stack ?? []).join(', '),
  }
}

function startAddWorkExp() {
  editingWorkExpId.value = 'new'
  workExpForm.value = { company: '', title: '', start_date: '', end_date: '', description: '', tech_stack: '' }
}

async function saveWorkExp() {
  if (!resumeDetailId.value) return
  savingWorkExp.value = true
  const payload = {
    company: workExpForm.value.company,
    title: workExpForm.value.title || null,
    start_date: workExpForm.value.start_date || null,
    end_date: workExpForm.value.end_date || null,
    description: workExpForm.value.description || null,
    tech_stack: workExpForm.value.tech_stack ? workExpForm.value.tech_stack.split(',').map(s => s.trim()).filter(Boolean) : [],
  }
  try {
    const rid = resumeDetailId.value
    if (editingWorkExpId.value === 'new') {
      const created = await postWithAuth<{ id: number; company: string; title?: string | null; start_date?: string | null; end_date?: string | null; description?: string | null; tech_stack?: string[]; resume_id: number; sort_order: number }>(`/resume/${rid}/work-experience/add`, payload)
      resumeDetail.value!.work_experiences = [...(resumeDetail.value!.work_experiences ?? []), created]
    } else {
      await postWithAuth(`/resume/${rid}/work-experience/${editingWorkExpId.value}/update`, payload)
      const list = resumeDetail.value!.work_experiences ?? []
      const idx = list.findIndex(w => w.id === editingWorkExpId.value)
      if (idx !== -1) list[idx] = { ...list[idx], ...payload }
    }
    editingWorkExpId.value = null
  } catch (e) {
    resumeModalError.value = e instanceof Error ? e.message : '保存失败'
  } finally {
    savingWorkExp.value = false
  }
}

async function deleteWorkExp(expId: number) {
  if (!resumeDetailId.value || !await showConfirm('删除工作经历', '确认删除该条工作经历？')) return
  try {
    await postWithAuth(`/resume/${resumeDetailId.value}/work-experience/${expId}/delete`)
    resumeDetail.value!.work_experiences = (resumeDetail.value!.work_experiences ?? []).filter(w => w.id !== expId)
  } catch (e) {
    resumeModalError.value = e instanceof Error ? e.message : '删除失败'
  }
}

// ── 教育经历操作 ────────────────────────────────────────────
function startEditEdu(e: { id?: number; school: string; degree?: string | null; major?: string | null; graduation_year?: string | null }) {
  if (e.id == null) {
    resumeModalError.value = '教育经历 ID 缺失，请关闭后重新打开详情页再编辑'
    return
  }
  editingEduId.value = e.id
  eduForm.value = { school: e.school, degree: e.degree ?? '', major: e.major ?? '', graduation_year: e.graduation_year ?? '' }
}

function startAddEdu() {
  editingEduId.value = 'new'
  eduForm.value = { school: '', degree: '', major: '', graduation_year: '' }
}

async function saveEdu() {
  if (!resumeDetailId.value) return
  savingEdu.value = true
  const payload = {
    school: eduForm.value.school,
    degree: eduForm.value.degree || null,
    major: eduForm.value.major || null,
    graduation_year: eduForm.value.graduation_year || null,
  }
  try {
    const rid = resumeDetailId.value
    if (editingEduId.value === 'new') {
      const created = await postWithAuth<{ id: number; school: string; degree?: string | null; major?: string | null; graduation_year?: string | null }>(`/resume/${rid}/education/add`, payload)
      resumeDetail.value!.educations = [...(resumeDetail.value!.educations ?? []), created]
    } else {
      await postWithAuth(`/resume/${rid}/education/${editingEduId.value}/update`, payload)
      const list = resumeDetail.value!.educations ?? []
      const idx = list.findIndex(e => e.id === editingEduId.value)
      if (idx !== -1) list[idx] = { ...list[idx], ...payload }
    }
    editingEduId.value = null
  } catch (e) {
    resumeModalError.value = e instanceof Error ? e.message : '保存失败'
  } finally {
    savingEdu.value = false
  }
}

async function deleteEdu(eduId: number) {
  if (!resumeDetailId.value || !await showConfirm('删除教育经历', '确认删除该条教育经历？')) return
  try {
    await postWithAuth(`/resume/${resumeDetailId.value}/education/${eduId}/delete`)
    resumeDetail.value!.educations = (resumeDetail.value!.educations ?? []).filter(e => e.id !== eduId)
  } catch (e) {
    resumeModalError.value = e instanceof Error ? e.message : '删除失败'
  }
}

// ── 项目经历操作 ────────────────────────────────────────────
function startEditProject(p: { id?: number; name: string; role?: string | null; start_date?: string | null; end_date?: string | null; description?: string | null; tech_stack?: string[] }) {
  if (p.id == null) {
    resumeModalError.value = '项目 ID 缺失，请关闭后重新打开详情页再编辑'
    return
  }
  editingProjectId.value = p.id
  projectForm.value = {
    name: p.name,
    role: p.role ?? '',
    start_date: p.start_date ?? '',
    end_date: p.end_date ?? '',
    description: p.description ?? '',
    tech_stack: (p.tech_stack ?? []).join(', '),
  }
}

function startAddProject() {
  editingProjectId.value = 'new'
  projectForm.value = { name: '', role: '', start_date: '', end_date: '', description: '', tech_stack: '' }
}

async function saveProject() {
  if (!resumeDetailId.value) return
  savingProject.value = true
  const payload = {
    name: projectForm.value.name,
    role: projectForm.value.role || null,
    start_date: projectForm.value.start_date || null,
    end_date: projectForm.value.end_date || null,
    description: projectForm.value.description || null,
    tech_stack: projectForm.value.tech_stack ? projectForm.value.tech_stack.split(',').map(s => s.trim()).filter(Boolean) : [],
  }
  try {
    const rid = resumeDetailId.value
    if (editingProjectId.value === 'new') {
      const created = await postWithAuth<{ id: number; name: string; role?: string | null; start_date?: string | null; end_date?: string | null; description?: string | null; tech_stack?: string[]; resume_id: number; sort_order: number }>(`/resume/${rid}/project/add`, payload)
      resumeDetail.value!.projects = [...(resumeDetail.value!.projects ?? []), created]
    } else {
      await postWithAuth(`/resume/${rid}/project/${editingProjectId.value}/update`, payload)
      const list = resumeDetail.value!.projects ?? []
      const idx = list.findIndex(p => p.id === editingProjectId.value)
      if (idx !== -1) list[idx] = { ...list[idx], ...payload }
    }
    editingProjectId.value = null
  } catch (e) {
    resumeModalError.value = e instanceof Error ? e.message : '保存失败'
  } finally {
    savingProject.value = false
  }
}

async function deleteProject(projectId: number) {
  if (!resumeDetailId.value || !await showConfirm('删除项目经历', '确认删除该条项目经历？')) return
  try {
    await postWithAuth(`/resume/${resumeDetailId.value}/project/${projectId}/delete`)
    resumeDetail.value!.projects = (resumeDetail.value!.projects ?? []).filter(p => p.id !== projectId)
  } catch (e) {
    resumeModalError.value = e instanceof Error ? e.message : '删除失败'
  }
}

async function postWithAuth<T = void>(path: string, body?: unknown): Promise<T> {
  const currentSession = loadAuthSession()
  if (!currentSession) throw new Error('未检测到登录状态')
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      Authorization: `${currentSession.token_type} ${currentSession.access_token}`,
      ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  const data = await response.json().catch(() => null)
  if (!response.ok) throw new Error(getApiErrorMessage(data, '请求失败'))
  return extractApiPayload<T>(data) as T
}

const profileName = computed(() => {
  const username = profileData.value?.username ?? session.value?.username ?? '用户'
  return String(username)
})

const userInitial = computed(() => profileName.value.slice(0, 1).toUpperCase())

const totalPoints = computed(() => {
  const rawValue = profileData.value?.total_points
  return typeof rawValue === 'number' ? rawValue : 0
})

type UserStats = { total_interviews: number; total_points: number; total_point_records: number }
const userStats = ref<UserStats>({ total_interviews: 0, total_points: 0, total_point_records: 0 })

const totalPages = computed(() => Math.max(1, Math.ceil(totalRecordCount.value / PAGE_SIZE)))
const pageStart = computed(() => (totalRecordCount.value === 0 ? 0 : (currentPage.value - 1) * PAGE_SIZE + 1))
const pageEnd = computed(() => Math.min(currentPage.value * PAGE_SIZE, totalRecordCount.value))
const resumeFileName = computed(() => {
  const data = profileData.value
  if (!data) return ''

  const directName = data.resume_file_name ?? data.resume_filename ?? data.cv_file_name
  if (typeof directName === 'string' && directName.trim()) return directName.trim()

  const fileUrl = data.resume_url ?? data.resume_file_url ?? data.cv_url
  if (typeof fileUrl === 'string' && fileUrl.trim()) {
    const normalized = fileUrl.split('?')[0]?.split('#')[0] ?? fileUrl
    const fileName = normalized.split('/').pop() ?? ''
    return fileName.trim()
  }

  return ''
})
const hasResume = computed(() => resumeFileName.value.length > 0)

const profileFields = computed<ProfileField[]>(() => {
  const data = profileData.value ?? {}

  return [
    { key: 'username', label: '用户名', value: formatValue(data.username) },
    { key: 'user_id', label: '用户 ID', value: formatValue(data.user_id) },
    { key: 'total_points', label: '当前积分', value: `${totalPoints.value} 分` },
  ]
})

const displayRecords = computed<DisplayPointRecord[]>(() =>
  pointRecords.value.map((record) => {
    const changePoint = toNumber(record.change_point)

    return {
      item: getRecordItem(record),
      changePoint,
      description: formatText(record.description, '暂无说明'),
      amount: getRecordAmount(record.amount),
      orderNo: formatText(record.order_no, '-'),
      createdAt: formatDateTime(record.created_at),
      sign: changePoint > 0 ? 'positive' : changePoint < 0 ? 'negative' : 'neutral',
    }
  }),
)

async function requestWithAuth<T>(path: string): Promise<T> {
  const currentSession = loadAuthSession()
  if (!currentSession) {
    throw new Error('未检测到登录状态，请先登录。')
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Authorization: `${currentSession.token_type} ${currentSession.access_token}`,
    },
  })

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(getApiErrorMessage(data, '请求失败，请稍后重试。'))
  }

  const payload = extractApiPayload<T>(data)
  if (payload === null) {
    throw new Error('请求失败：服务响应数据格式不正确。')
  }

  return payload
}

function normalizePointRecordResponse(payload: PointRecordListResponse | PointRecord[]) {
  if (Array.isArray(payload)) {
    return {
      items: payload,
      total: payload.length,
    }
  }

  if (payload && typeof payload === 'object') {
    if ('items' in payload && Array.isArray(payload.items)) {
      const response = payload as PointRecordListResponse
      return {
        items: response.items ?? [],
        total: typeof response.total === 'number' ? response.total : (response.items?.length ?? 0),
      }
    }

    return {
      items: [],
      total: 0,
    }
  }

  return {
    items: [],
    total: 0,
  }
}

function formatValue(value: unknown) {
  if (value === null || value === undefined || value === '') return '-'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

function formatText(value: unknown, fallback = '-') {
  if (value === null || value === undefined) return fallback
  const text = String(value).trim()
  return text || fallback
}

function toNumber(value: unknown) {
  if (typeof value === 'number') return value
  if (typeof value === 'string') {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : 0
  }

  return 0
}

function getRecordItem(record: PointRecord) {
  const item = formatText(record.item, '积分变动')
  return item.length > 12 ? item.slice(0, 12) : item
}

function getRecordAmount(amount: PointRecord['amount']) {
  if (amount === null || amount === undefined || amount === '') return '-'
  return String(amount)
}

function formatChangePoint(value: number) {
  if (value > 0) return `+${value}`
  return String(value)
}

function formatDateTime(value?: string) {
  if (!value) return '-'

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  const diffMs = Date.now() - date.getTime()
  const diffHours = diffMs / (1000 * 60 * 60)
  const diffDays = diffMs / (1000 * 60 * 60 * 24)

  if (diffHours < 24) {
    const hours = Math.floor(diffHours)
    return hours < 1 ? '刚刚' : `${hours}小时前`
  }

  if (diffDays < 3) {
    return `${Math.floor(diffDays)}天前`
  }

  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function triggerResumeUpload() {
  resumeUploadError.value = ''
  resumeFileInput.value?.click()
}

async function uploadResume(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  const currentSession = loadAuthSession()
  if (!currentSession) return

  resumeUploading.value = true
  resumeUploadError.value = ''

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${API_BASE_URL}/resume/parse`, {
      method: 'POST',
      headers: {
        Authorization: `${currentSession.token_type} ${currentSession.access_token}`,
      },
      body: formData,
    })

    const data = await response.json().catch(() => null)

    if (!response.ok) {
      throw new Error(getApiErrorMessage(data, '上传失败，请稍后重试。'))
    }

    // 立即刷新列表（pending 状态）
    const resumeId = extractApiPayload<number>(data) as number
    const list = await requestWithAuth<ResumeListItem[]>('/resume/list').catch(() => resumeList.value)
    resumeList.value = list

    addToast('info', `「${file.name}」上传成功，正在后台解析...`, 8000)
    startPolling(resumeId)
    // 上传后 resumeUploading 保持 true，直到轮询到结果才关闭
    return
  } catch (error) {
    resumeUploadError.value = error instanceof Error ? error.message : '上传失败，请稍后重试。'
    resumeUploading.value = false
  } finally {
    input.value = ''
  }
}

function logout() {
  clearAuthSession()
  router.push('/')
}

async function loadPointRecords() {
  const recordsResponse = await requestWithAuth<PointRecordListResponse | PointRecord[]>(
    `/user/point-record/list?offset=${currentPage.value}&limit=${PAGE_SIZE}`,
  )

  const normalized = normalizePointRecordResponse(recordsResponse)
  pointRecords.value = normalized.items
  totalRecordCount.value = normalized.total
}

async function loadProfilePage() {
  profileLoading.value = true
  profileError.value = ''

  try {
    session.value = loadAuthSession()
    if (!session.value) {
      router.push('/')
      return
    }

    const [meResponse] = await Promise.all([requestWithAuth<ProfileData>('/user/me')])

    profileData.value = meResponse
    await Promise.all([
      loadPointRecords(),
      requestWithAuth<ResumeListItem[]>('/resume/list').then(list => { resumeList.value = list }).catch(() => {}),
      requestWithAuth<UserStats>('/user/stats').then(stats => { userStats.value = stats }).catch(() => {}),
    ])
  } catch (error) {
    profileError.value =
      error instanceof Error ? error.message : '加载个人中心失败。'
  } finally {
    profileLoading.value = false
  }
}

onMounted(() => {
  loadProfilePage()
})

async function goToPage(page: number) {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return

  profileLoading.value = true
  profileError.value = ''
  currentPage.value = page

  try {
    await loadPointRecords()
  } catch (error) {
    profileError.value =
      error instanceof Error ? error.message : '加载积分记录失败。'
  } finally {
    profileLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen pb-32" style="background-color: #f8f9ff; color: #0b1c30;">
    <!-- Loading State -->
    <div v-if="profileLoading" style="display: flex; align-items: center; justify-content: center; min-height: 100vh; background-color: #f8f9ff;">
      <div style="text-align: center; display: flex; flex-direction: column; align-items: center; gap: 0;">

        <!-- 品牌图标 呼吸动画 -->
        <div class="logo-breathe" style="width: 64px; height: 64px; background: #00236f; border-radius: 18px; display: flex; align-items: center; justify-content: center; margin-bottom: 28px; box-shadow: 0 8px 32px rgba(0,35,111,0.22);">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white" style="width:32px;height:32px;transform:matrix(-1,0,0,1,0,0);">
            <path d="M13 8.57a1.43 1.43 0 1 0 0 2.86 1.43 1.43 0 0 0 0-2.86z"/>
            <path d="M13 3C9.25 3 6.2 5.94 6.02 9.64L4.1 12.2a.5.5 0 0 0 .4.8H6v3c0 1.1.9 2 2 2h1v3h7v-4.68A6.999 6.999 0 0 0 13 3zm3 7c0 .13-.01.26-.02.39l.83.66c.08.06.1.16.05.25l-.8 1.39c-.05.09-.16.12-.24.09l-.99-.4c-.21.16-.43.29-.67.39L14 13.83c-.01.1-.1.17-.2.17h-1.6c-.1 0-.18-.07-.2-.17l-.15-1.06c-.25-.1-.47-.23-.68-.39l-.99.4c-.09.03-.2 0-.25-.09l-.8-1.39a.19.19 0 0 1 .05-.25l.84-.66c-.01-.13-.02-.26-.02-.39s.02-.27.04-.39l-.85-.66c-.08-.06-.1-.16-.05-.26l.8-1.38c.05-.09.15-.12.24-.09l1 .4c.2-.15.43-.29.67-.39L12 6.17c.02-.1.1-.17.2-.17h1.6c.1 0 .18.07.2.17l.15 1.06c.24.1.46.23.67.39l1-.4c.09-.03.2 0 .24.09l.8 1.38a.2.2 0 0 1-.05.26l-.85.66c.03.12.04.25.04.39z"/>
          </svg>
        </div>

        <!-- 三点波浪 -->
        <div style="display: flex; gap: 7px; justify-content: center; margin-bottom: 20px;">
          <span class="dot dot-1"></span>
          <span class="dot dot-2"></span>
          <span class="dot dot-3"></span>
        </div>

        <p style="font-family: 'Inter', sans-serif; color: #8c93a8; font-size: 13px; letter-spacing: 0.03em;">正在加载个人中心</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="profileError" style="display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 0 24px;">
      <div style="background: #ffffff; border-radius: 16px; padding: 40px 36px; text-align: center; width: 400px; max-width: calc(100vw - 48px); box-shadow: 0 4px 24px rgba(30,58,138,0.08); border-top: 4px solid #ba1a1a;">
        <div style="width: 56px; height: 56px; background: #fff1f1; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
          <svg t="1778503795609" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="28" height="28">
            <path d="M753.845117 371.674021l-17.46272 0 0-83.669608c0-59.275012-22.62837-115.203812-63.715137-157.482731-42.170448-43.394323-99.369172-67.291592-161.058163-67.291592-126.040624 0-224.772276 98.731652-224.772276 224.7733l0 83.669608-16.680914 0c-62.788022 0-113.688295 50.900274-113.688295 113.688295L156.467611 842.961784c0 62.788022 50.900274 113.688295 113.688295 113.688295l483.690234 0c62.788022 0 113.688295-50.900274 113.688295-113.688295L867.534436 485.362316C867.532389 422.574295 816.633139 371.674021 753.845117 371.674021zM328.176344 288.005436c0-102.858646 80.573083-183.432753 183.431729-183.432753 50.423413 0 97.093339 19.447934 131.410935 54.762231 33.547047 34.519188 52.021817 80.214926 52.021817 128.670521l0 83.669608L328.176344 371.675044 328.176344 288.005436zM826.191842 842.961784c0 39.956014-32.390711 72.346725-72.346725 72.346725L270.154883 915.308509c-39.956014 0-72.346725-32.390711-72.346725-72.346725L197.808158 485.362316c0-39.956014 32.390711-72.346725 72.346725-72.346725l483.690234 0c39.956014 0 72.346725 32.390711 72.346725 72.346725L826.191842 842.961784z" fill="#ba1a1a"/>
            <path d="M509.932921 580.446905c-11.416004 0-20.670785 9.254781-20.670785 20.670785l0 109.554138c0 11.414981 9.254781 20.670785 20.670785 20.670785 11.416004 0 20.670785-9.254781 20.670785-20.670785L530.603707 601.116667C530.602683 589.701686 521.348925 580.446905 509.932921 580.446905z" fill="#ba1a1a"/>
          </svg>
        </div>
        <h3 style="font-size: 17px; font-weight: 600; color: #0b1c30; margin: 0 0 8px; font-family: 'Inter', sans-serif;">登录已失效</h3>
        <p style="font-size: 14px; color: #6b7280; margin: 0 0 28px; line-height: 1.6; font-family: 'Inter', sans-serif;">{{ profileError }}</p>
        <div style="display: flex; gap: 12px; justify-content: center;">
          <button @click="router.push('/login')"
                  style="padding: 10px 24px; border-radius: 8px; font-size: 14px; font-weight: 600; background-color: #00236f; color: #ffffff; border: none; cursor: pointer; font-family: 'Inter', sans-serif; transition: opacity 0.15s;"
                  onmouseover="this.style.opacity='0.85'" onmouseout="this.style.opacity='1'">
            重新登录
          </button>
          <button @click="loadProfilePage"
                  style="padding: 10px 24px; border-radius: 8px; font-size: 14px; font-weight: 600; background-color: #f3f4f6; color: #374151; border: none; cursor: pointer; font-family: 'Inter', sans-serif; transition: opacity 0.15s;"
                  onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'">
            重试
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main v-else class="pt-24 max-w-screen-xl mx-auto px-6 grid grid-cols-1 md:grid-cols-12 gap-6">

      <!-- Profile Header Section -->
      <section class="md:col-span-12 rounded-xl p-6 flex flex-col md:flex-row items-center gap-6"
               style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
        <!-- Avatar -->
        <div class="relative flex-shrink-0">
          <img v-if="profileData?.avatar_url"
               :src="profileData.avatar_url"
               alt="User Profile"
               class="w-32 h-32 rounded-full"
               style="border: 4px solid rgba(0,35,111,0.1);" />
          <div v-else
               class="w-32 h-32 rounded-full flex items-center justify-center"
               style="background-color: #1e3a8a; border: 4px solid rgba(0,35,111,0.1);">
            <span class="font-bold text-4xl" style="color: #90a8ff; font-family: 'Inter', sans-serif;">{{ userInitial }}</span>
          </div>
          <!-- Verified Badge -->
          <div class="absolute bottom-0 right-0 p-1 rounded-full"
               style="background-color: #006c49; border: 2px solid #ffffff;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px;color:#ffffff;display:block;">
              <path d="m23 12-2.44-2.79.34-3.69-3.61-.82-1.89-3.2L12 2.96 8.6 1.5 6.71 4.69 3.1 5.5l.34 3.7L1 12l2.44 2.79-.34 3.7 3.61.82L8.6 22.5l3.4-1.47 3.4 1.46 1.89-3.19 3.61-.82-.34-3.69L23 12zm-12.91 4.72-3.8-3.81 1.48-1.48 2.32 2.33 5.85-5.87 1.48 1.48-7.33 7.35z"></path>
            </svg>
          </div>
        </div>

        <!-- Name & Info -->
        <div class="text-center md:text-left flex-1">
          <h2 class="font-semibold mb-2" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #0b1c30;">
            {{ profileName }}
          </h2>
          <div class="flex flex-wrap justify-center md:justify-start gap-2 mt-2">
            <span v-for="field in profileFields" :key="field.key"
                  class="px-3 py-1 rounded-full text-xs font-semibold tracking-widest"
                  style="font-family: 'JetBrains Mono', monospace; background-color: #dce9ff; color: #444651;">
              {{ field.label }}: {{ field.value }}
            </span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-col gap-3 w-full md:w-auto">
          <RouterLink to="/interview/setup"
                      class="flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all active:scale-95 whitespace-nowrap"
                      style="background-color: #00236f; color: #ffffff; font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px;flex-shrink:0;">
              <path d="M13 7h-2v4H7v2h4v4h2v-4h4v-2h-4V7zm-1-5C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"></path>
            </svg>
            开始新面试
          </RouterLink>
          <RouterLink to="/results"
                      class="flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all active:scale-95 whitespace-nowrap"
                      style="background: transparent; border: 1px solid #00236f; color: #00236f; font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px;flex-shrink:0;">
              <path d="M13 3a9 9 0 0 0-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42A8.954 8.954 0 0 0 13 21a9 9 0 0 0 0-18zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z"></path>
            </svg>
            查看详细历史
          </RouterLink>
        </div>
      </section>

      <!-- Growth Stats Bento -->
      <section class="md:col-span-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Sessions Card -->
        <div class="rounded-xl p-6 flex items-center gap-6"
             style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
          <div class="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style="background-color: #dce1ff; color: #00236f;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:32px;height:32px;">
              <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-3 11-2-1.99V13c0 .55-.45 1-1 1H8c-.55 0-1-.45-1-1V7c0-.55.45-1 1-1h6c.55 0 1 .45 1 1v1.99L17 7v6z"></path>
            </svg>
          </div>
          <div>
            <p class="text-xs font-semibold tracking-widest uppercase mb-1" style="font-family: 'JetBrains Mono', monospace; color: #444651;">总面试次数</p>
            <p class="font-semibold" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #0b1c30;">{{ userStats.total_interviews }}</p>
          </div>
        </div>

        <!-- Avg Score Card -->
        <div class="rounded-xl p-6 flex items-center gap-6"
             style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
          <div class="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style="background-color: #6cf8bb; color: #006c49;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:32px;height:32px;">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"></path>
              <path d="M7 12h2v5H7zm8-5h2v10h-2zm-4 7h2v3h-2zm0-4h2v2h-2z"></path>
            </svg>
          </div>
          <div>
            <p class="text-xs font-semibold tracking-widest uppercase mb-1" style="font-family: 'JetBrains Mono', monospace; color: #444651;">当前积分</p>
            <p class="font-semibold" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #0b1c30;">
              {{ userStats.total_points }}<span class="font-normal" style="font-size: 24px; line-height: 1.3;"> 分</span>
            </p>
          </div>
        </div>

        <!-- Points Card -->
        <div class="rounded-xl p-6 flex items-center gap-6"
             style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); border: 2px solid rgba(0,35,111,0.1); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
          <div class="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style="background-color: #e1e0ff; color: #0d0097;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:32px;height:32px;">
              <path d="M17 10.43V2H7v8.43c0 .35.18.68.49.86l4.18 2.51-.99 2.34-3.41.29 2.59 2.24L9.07 22 12 20.23 14.93 22l-.78-3.33 2.59-2.24-3.41-.29-.99-2.34 4.18-2.51c.3-.18.48-.5.48-.86zm-6 .64-2-1.2V4h2v7.07zm4-1.2-2 1.2V4h2v5.87z"></path>
            </svg>
          </div>
          <div>
            <p class="text-xs font-semibold tracking-widest uppercase mb-1" style="font-family: 'JetBrains Mono', monospace; color: #444651;">积分记录条数</p>
            <p class="font-semibold" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #0b1c30;">{{ userStats.total_point_records }}</p>
          </div>
        </div>
      </section>

      <!-- Main Content Area (Points Records) -->
      <section class="md:col-span-8 flex flex-col gap-6">
        <div class="rounded-xl overflow-hidden"
             style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
          <!-- Card Header -->
          <div class="p-6 flex justify-between items-center" style="border-bottom: 1px solid rgba(197,197,211,0.2);">
            <h3 class="font-semibold flex items-center gap-3" style="font-family: 'Inter', sans-serif; font-size: 24px; line-height: 1.3; color: #0b1c30;">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:22px;height:22px;color:#00236f;flex-shrink:0;">
                <path d="M19.5 3.5 18 2l-1.5 1.5L15 2l-1.5 1.5L12 2l-1.5 1.5L9 2 7.5 3.5 6 2v14H3v3c0 1.66 1.34 3 3 3h12c1.66 0 3-1.34 3-3V2l-1.5 1.5zM15 20H6c-.55 0-1-.45-1-1v-1h10v2zm4-1c0 .55-.45 1-1 1s-1-.45-1-1v-3H8V5h11v14z"></path>
                <path d="M9 7h6v2H9zm7 0h2v2h-2zm-7 3h6v2H9zm7 0h2v2h-2z"></path>
              </svg>
              积分记录
            </h3>
            <span class="text-sm font-semibold" style="color: #00236f; font-family: 'Inter', sans-serif; cursor: pointer;">
              共 {{ totalRecordCount }} 条
            </span>
          </div>

          <!-- Records List -->
          <div v-if="displayRecords.length" style="divide-y: 1px solid rgba(197,197,211,0.1);">
            <div v-for="(record, index) in displayRecords"
                 :key="`${record.createdAt}-${record.orderNo}-${index}`"
                 class="p-6 flex items-center justify-between transition-colors"
                 style="border-bottom: 1px solid rgba(197,197,211,0.1);"
                 onmouseover="this.style.backgroundColor='rgba(239,244,255,0.5)'"
                 onmouseout="this.style.backgroundColor='transparent'">
              <div class="flex items-center gap-6">
                <!-- Icon -->
                <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0" style="background-color: #d3e4fe;">
                  <svg v-if="record.sign === 'positive'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;color:#00236f;">
                    <path d="M13 7h-2v4H7v2h4v4h2v-4h4v-2h-4V7zm-1-5C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"></path>
                  </svg>
                  <span v-else class="material-symbols-outlined" style="color: #00236f; font-size: 20px;">
                    {{ record.sign === 'negative' ? 'remove_circle' : 'circle' }}
                  </span>
                </div>
                <!-- Info -->
                <div>
                  <h4 class="font-semibold mb-1" style="font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1.6; color: #0b1c30;">{{ record.item }}</h4>
                  <p class="text-sm" style="font-family: 'Inter', sans-serif; color: #444651;">{{ record.description }} · {{ record.createdAt }}</p>
                </div>
              </div>

              <!-- Score & Arrow -->
              <div class="flex items-center gap-6">
                <div class="text-right">
                  <p class="text-xs font-semibold tracking-widest uppercase"
                     :style="record.sign === 'positive' ? 'color: #006c49;' : record.sign === 'negative' ? 'color: #ba1a1a;' : 'color: #444651;'"
                     style="font-family: 'JetBrains Mono', monospace;">
                    {{ record.sign === 'positive' ? '增加' : record.sign === 'negative' ? '减少' : '中性' }}
                  </p>
                  <p class="font-semibold"
                     :style="record.sign === 'positive' ? 'color: #006c49;' : record.sign === 'negative' ? 'color: #ba1a1a;' : 'color: #444651;'"
                     style="font-family: 'Inter', sans-serif; font-size: 24px; line-height: 1.3;">
                    {{ formatChangePoint(record.changePoint) }}
                  </p>
                </div>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px;color:#757682;flex-shrink:0;">
                  <path d="M10 6 8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"></path>
                </svg>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="p-12 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:48px;height:48px;color:#c5c5d3;display:block;margin:0 auto 16px;">
              <path d="M19.5 3.5 18 2l-1.5 1.5L15 2l-1.5 1.5L12 2l-1.5 1.5L9 2 7.5 3.5 6 2v14H3v3c0 1.66 1.34 3 3 3h12c1.66 0 3-1.34 3-3V2l-1.5 1.5zM15 20H6c-.55 0-1-.45-1-1v-1h10v2zm4-1c0 .55-.45 1-1 1s-1-.45-1-1v-3H8V5h11v14z"></path>
              <path d="M9 7h6v2H9zm7 0h2v2h-2zm-7 3h6v2H9zm7 0h2v2h-2z"></path>
            </svg>
            <p style="font-family: 'Inter', sans-serif; color: #757682;">暂无积分记录。</p>
          </div>

          <!-- Pagination Footer -->
          <div class="p-6 flex flex-col sm:flex-row justify-between items-center gap-4" style="border-top: 1px solid rgba(197,197,211,0.1);">
            <span class="text-sm" style="font-family: 'Inter', sans-serif; color: #444651;">
              总计 {{ totalRecordCount }} 条，当前显示 {{ pageStart }}-{{ pageEnd }} 条
            </span>
            <div class="flex items-center gap-3">
              <button
                type="button"
                class="px-4 py-2 rounded-lg text-sm font-semibold transition-all active:scale-95"
                :disabled="currentPage <= 1"
                :style="currentPage <= 1 ? 'background-color: #d3e4fe; color: #c5c5d3; cursor: not-allowed;' : 'background-color: #dce9ff; color: #00236f; cursor: pointer;'"
                style="font-family: 'Inter', sans-serif;"
                @click="goToPage(currentPage - 1)">
                上一页
              </button>
              <span class="text-sm font-semibold" style="font-family: 'JetBrains Mono', monospace; color: #444651;">
                {{ currentPage }} / {{ totalPages }}
              </span>
              <button
                type="button"
                class="px-4 py-2 rounded-lg text-sm font-semibold transition-all active:scale-95"
                :disabled="currentPage >= totalPages"
                :style="currentPage >= totalPages ? 'background-color: #d3e4fe; color: #c5c5d3; cursor: not-allowed;' : 'background-color: #dce9ff; color: #00236f; cursor: pointer;'"
                style="font-family: 'Inter', sans-serif;"
                @click="goToPage(currentPage + 1)">
                下一页
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Sidebar -->
      <aside class="md:col-span-4 flex flex-col gap-6">

        <!-- Resume Management -->
        <div class="rounded-xl p-6"
             style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
          <h3 class="font-semibold flex items-center gap-2 mb-6" style="font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1.6; color: #0b1c30;">
            <svg t="1778306048835" class="icon" viewBox="0 0 1707 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" style="width:18px;height:18px;flex-shrink:0;">
              <path d="M496.4356 44.505433c-26.753266 0-44.505433 17.752167-44.505433 44.505433v845.978268c0 26.753266 17.752167 44.505433 44.505433 44.505433H1208.897571c26.753266 0 44.505433-17.752167 44.505432-44.505433V89.135881c0-26.753266-17.752167-44.505433-44.505432-44.505433H496.4356z m0-44.505433H1208.897571c49.005982 0 89.010866 40.129899 89.010865 89.010866v845.978268c0 49.005982-40.129899 89.010866-89.010865 89.010866H496.4356c-49.005982 0-89.010866-40.129899-89.010866-89.010866V89.135881c0-49.005982 40.004883-89.135881 89.010866-89.135881z m0 0" fill="#61C6F1"></path>
              <path d="M696.835063 578.820657c0 13.376633-8.876084 22.252716-22.252717 22.252716-13.376633 0-22.252716-8.876084-22.252716-22.252716 0-120.264681 75.634233-244.904896 200.399463-244.904896 124.640215 0 191.523379 115.764131 191.523379 244.904896 0 13.376633-8.876084 22.252716-22.252716 22.252716-13.376633 0-22.252716-8.876084-22.252717-22.252716 0-106.888048-53.381516-200.399463-146.892931-200.399463-93.63643 0.125015-156.019045 102.512514-156.019045 200.399463z m0 0" fill="#999999"></path>
              <path d="M852.729093 378.546209c-62.382615 0-111.263582-49.005982-111.263582-111.263582 0-62.382615 49.005982-111.263582 111.263582-111.263582 62.382615 0 111.263582 49.005982 111.263582 111.263582s-49.005982 111.263582-111.263582 111.263582z m0-44.630448c35.629349 0 66.758149-31.1288 66.758149-66.758149s-31.1288-66.758149-66.758149-66.758149-66.758149 31.1288-66.758149 66.758149c-0.125015 35.629349 31.1288 66.758149 66.758149 66.758149zM563.193749 712.46197c-13.376633 0-22.252716-8.876084-22.252716-22.252716 0-13.376633 8.876084-22.252716 22.252716-22.252716H1097.633989c13.376633 0 22.252716 8.876084 22.252716 22.252716 0 13.376633-8.876084 22.252716-22.252716 22.252716H563.193749z m0 133.516299c-13.376633 0-22.252716-8.876084-22.252716-22.252717 0-13.376633 8.876084-22.252716 22.252716-22.252716H1097.633989c13.376633 0 22.252716 8.876084 22.252716 22.252716 0 13.376633-8.876084 22.252716-22.252716 22.252717H563.193749z m0 0" fill="#999999"></path>
            </svg>
            简历管理
          </h3>
          <input
            ref="resumeFileInput"
            type="file"
            accept=".pdf"
            style="display: none;"
            @change="uploadResume"
          />
          <!-- 有简历：展示第一条 -->
          <div v-if="resumeList.length && !resumeUploading"
               class="rounded-lg p-4 mb-6 flex items-center gap-3 cursor-pointer transition-colors"
               style="background-color: #ffffff; border: 2px solid #dce9ff;"
               onmouseover="this.style.borderColor='#00236f'"
               onmouseout="this.style.borderColor='#dce9ff'"
               @click="openResumeModal">
            <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style="background:#dce9ff;">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;color:#00236f;">
                <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
              </svg>
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold truncate" style="font-family:'Inter',sans-serif;color:#0b1c30;">{{ resumeList[0].file_name }}</p>
              <p class="text-xs mt-0.5" style="font-family:'Inter',sans-serif;color:#757682;">
                {{ resumeList[0].name ?? '未识别姓名' }} · {{ formatDateTime(resumeList[0].created_at) }}
              </p>
            </div>
            <span class="px-2 py-0.5 rounded-full text-xs font-semibold flex-shrink-0"
                  style="background:#d1fae5;color:#065f46;font-family:'Inter',sans-serif;">已解析</span>
          </div>
          <!-- 无简历或上传中 -->
          <div v-else
               class="rounded-lg p-6 text-center mb-6"
               style="background-color: #ffffff; border: 2px dashed #c5c5d3;">
            <!-- 上传动画 -->
            <div v-if="resumeUploading" style="position:relative;width:60px;height:60px;margin:0 auto 8px;">
              <!-- 绕圈小长条 -->
              <svg viewBox="0 0 60 60" style="position:absolute;inset:0;width:60px;height:60px;" class="resume-orbit">
                <circle cx="30" cy="30" r="28"
                        fill="none"
                        stroke="#6cf8bb"
                        stroke-width="3"
                        stroke-linecap="round"
                        stroke-dasharray="44 132"/>
              </svg>
              <!-- 云图标 -->
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"
                   style="position:absolute;inset:0;margin:auto;width:34px;height:34px;top:50%;left:50%;transform:translate(-50%,-50%);color:#00236f;">
                <path d="M19.35 10.04A7.49 7.49 0 0 0 12 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 0 0 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM19 18H6c-2.21 0-4-1.79-4-4 0-2.05 1.53-3.76 3.56-3.97l1.07-.11.5-.95A5.469 5.469 0 0 1 12 6c2.62 0 4.88 1.86 5.39 4.43l.3 1.5 1.53.11A2.98 2.98 0 0 1 22 15c0 1.65-1.35 3-3 3zM8 13h2.55v3h2.9v-3H16l-4-4z"/>
              </svg>
            </div>
            <!-- 无简历静态图标 -->
            <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="mb-2 block mx-auto" style="width:40px;height:40px;color:rgba(0,35,111,0.3);">
              <path d="M19.35 10.04A7.49 7.49 0 0 0 12 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 0 0 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM19 18H6c-2.21 0-4-1.79-4-4 0-2.05 1.53-3.76 3.56-3.97l1.07-.11.5-.95A5.469 5.469 0 0 1 12 6c2.62 0 4.88 1.86 5.39 4.43l.3 1.5 1.53.11A2.98 2.98 0 0 1 22 15c0 1.65-1.35 3-3 3zM8 13h2.55v3h2.9v-3H16l-4-4z"></path>
            </svg>
            <p v-if="resumeUploading" class="text-xs font-semibold" style="font-family:'Inter',sans-serif;color:#00236f;">正在解析中...</p>
            <p v-else class="text-xs" style="font-family:'Inter',sans-serif;color:#444651;">暂未上传简历</p>
            <p v-if="resumeUploadError" class="text-xs mt-2" style="font-family:'Inter',sans-serif;color:#ba1a1a;">{{ resumeUploadError }}</p>
          </div>
          <div class="flex flex-col gap-2">
            <button
              class="w-full py-2 rounded-lg text-sm font-semibold transition-colors"
              :disabled="resumeUploading"
              :style="resumeUploading ? 'background-color:#d3e4fe;color:#c5c5d3;cursor:not-allowed;font-family:Inter,sans-serif;' : 'background-color:#dce9ff;color:#444651;cursor:pointer;font-family:Inter,sans-serif;'"
              @click="triggerResumeUpload">
              {{ resumeUploading ? '解析中...' : hasResume ? '替换文件' : '上传简历' }}
            </button>
            <button class="w-full py-2 rounded-lg text-sm font-semibold transition-colors"
                    style="background: transparent; color: #00236f; font-family: 'Inter', sans-serif;"
                    onmouseover="this.style.backgroundColor='rgba(0,35,111,0.05)'"
                    onmouseout="this.style.backgroundColor='transparent'"
                    @click="openResumeModal">
              查看解析
            </button>
          </div>
        </div>

        <!-- Motivational Card -->
        <div class="rounded-xl p-6 relative overflow-hidden"
             style="background: linear-gradient(135deg, #1e3a8a 0%, #00236f 100%); color: #90a8ff;">
          <div class="relative z-10">
            <h4 class="font-semibold mb-2" style="font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1.6; color: #dce1ff;">面试准备好了吗？</h4>
            <p class="text-sm mb-6" style="font-family: 'Inter', sans-serif; color: rgba(220,225,255,0.9); line-height: 1.6;">您本周在候选人中排名前 5%！继续保持，提升你的竞争力。</p>

            <!-- Progress Bar -->
            <div class="rounded-full overflow-hidden mb-2" style="height: 8px; background: rgba(255,255,255,0.2);">
              <div class="h-full rounded-full" style="background-color: #6ffbbe; width: 85%;"></div>
            </div>
            <p class="text-xs font-semibold tracking-widest uppercase" style="font-family: 'JetBrains Mono', monospace; color: rgba(220,225,255,0.7);">连续练习天数：5天</p>
          </div>
          <span class="material-symbols-outlined absolute -bottom-4 -right-4 pointer-events-none"
                style="font-size: 120px; color: rgba(255,255,255,0.08);">trending_up</span>
        </div>

        <!-- Logout Button -->
        <button @click="logout"
                class="w-full flex items-center justify-center gap-2 py-3 rounded-lg font-semibold transition-all active:scale-95"
                style="background: transparent; border: 1px solid rgba(186,26,26,0.3); color: #ba1a1a; font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1;">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px;flex-shrink:0;">
            <path d="m17 7-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"></path>
          </svg>
          退出登录
        </button>
      </aside>

    </main>

    <!-- Resume Modal -->
    <div v-if="resumeModalOpen"
         class="fixed inset-0 z-50 flex items-center justify-center"
         style="background: rgba(11,28,48,0.5); backdrop-filter: blur(4px);">
      <div class="rounded-2xl w-full mx-4 overflow-hidden flex flex-col"
           style="max-width: 560px; max-height: 85vh; background: #ffffff; box-shadow: 0 24px 64px rgba(11,28,48,0.18);">

        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4" style="border-bottom: 1px solid #f0f0f5;">
          <div class="flex items-center gap-2">
            <button v-if="resumeDetail" @click="backToList"
                    style="color:#00236f;background:none;border:none;cursor:pointer;padding:2px;display:flex;align-items:center;">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px;">
                <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
              </svg>
            </button>
            <h3 class="font-semibold" style="font-family:'Inter',sans-serif;font-size:16px;color:#0b1c30;">
              {{ resumeDetail ? (isEditing ? '编辑简历' : '解析详情') : '我的简历' }}
            </h3>
          </div>
          <div class="flex items-center gap-2">
            <!-- 详情页：编辑 / 保存 / 取消 -->
            <template v-if="resumeDetail && !resumeModalLoading">
              <template v-if="!isEditing">
                <button @click="startEditing"
                        class="px-3 py-1 rounded-lg text-xs font-semibold"
                        style="background:#dce9ff;color:#00236f;border:none;cursor:pointer;font-family:'Inter',sans-serif;">
                  编辑
                </button>
              </template>
              <template v-else>
                <button @click="saveEdit" :disabled="isSaving"
                        class="px-3 py-1 rounded-lg text-xs font-semibold"
                        :style="isSaving ? 'background:#d3e4fe;color:#c5c5d3;cursor:not-allowed;border:none;font-family:Inter,sans-serif;' : 'background:#00236f;color:#fff;cursor:pointer;border:none;font-family:Inter,sans-serif;'">
                  {{ isSaving ? '保存中...' : '保存' }}
                </button>
                <button @click="isEditing = false" :disabled="isSaving"
                        class="px-3 py-1 rounded-lg text-xs font-semibold"
                        style="background:#f0f0f5;color:#444651;border:none;cursor:pointer;font-family:'Inter',sans-serif;">
                  取消
                </button>
              </template>
            </template>
            <button @click="closeResumeModal"
                    style="color:#757682;background:none;border:none;cursor:pointer;padding:4px;">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;">
                <path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Loading -->
        <div v-if="resumeModalLoading" class="flex items-center justify-center py-16">
          <div style="display:flex;flex-direction:column;align-items:center;gap:12px;">
            <div style="display:flex;gap:7px;">
              <span class="dot dot-1"></span><span class="dot dot-2"></span><span class="dot dot-3"></span>
            </div>
            <p style="font-family:'Inter',sans-serif;color:#8c93a8;font-size:13px;">正在加载...</p>
          </div>
        </div>

        <!-- Error -->
        <div v-else-if="resumeModalError" class="px-6 py-10 text-center">
          <p style="font-family:'Inter',sans-serif;color:#ba1a1a;font-size:14px;">{{ resumeModalError }}</p>
          <button v-if="resumeDetail" @click="backToList" class="mt-4 text-sm" style="color:#00236f;background:none;border:none;cursor:pointer;">返回列表</button>
        </div>

        <!-- 列表视图 -->
        <div v-else-if="!resumeDetail" class="overflow-y-auto">
          <div v-if="!resumeList.length" class="px-6 py-12 text-center">
            <p style="font-family:'Inter',sans-serif;color:#757682;font-size:14px;">暂无已解析的简历</p>
          </div>
          <div v-for="item in resumeList" :key="item.id"
               class="flex items-center justify-between px-6 py-4 cursor-pointer transition-colors"
               style="border-bottom:1px solid #f0f0f5;"
               onmouseover="this.style.background='#f8faff'"
               onmouseout="this.style.background=''"
               @click="openResumeDetail(item.id)">
            <div class="flex items-center gap-3 min-w-0">
              <!-- 文件图标 -->
              <div class="flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center" style="background:#dce9ff;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px;color:#00236f;">
                  <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"/>
                </svg>
              </div>
              <div class="min-w-0">
                <p class="text-sm font-semibold truncate" style="font-family:'Inter',sans-serif;color:#0b1c30;">{{ item.file_name }}</p>
                <p class="text-xs" style="font-family:'Inter',sans-serif;color:#757682;">
                  {{ item.name ?? '未识别姓名' }} · {{ formatDateTime(item.created_at) }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0 ml-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-semibold"
                    :style="item.parse_status === 'success' ? 'background:#d1fae5;color:#065f46;' : 'background:#fee2e2;color:#991b1b;'">
                {{ item.parse_status === 'success' ? '已解析' : item.parse_status }}
              </span>
              <!-- 删除按钮 -->
              <button @click.stop="deleteResume(item.id)"
                      :disabled="deletingId === item.id"
                      style="background:none;border:none;cursor:pointer;color:#ba1a1a;padding:4px;display:flex;align-items:center;"
                      title="删除">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:16px;height:16px;">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              </button>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:16px;height:16px;color:#c5c5d3;">
                <path d="M10 6 8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- 详情视图 -->
        <div v-else class="overflow-y-auto px-6 py-4 flex flex-col gap-5">
          <!-- Basic Info - 查看模式 -->
          <div v-if="!isEditing">
            <p class="text-xs font-semibold tracking-widest uppercase mb-3" style="font-family:'JetBrains Mono',monospace;color:#444651;">基本信息</p>
            <div class="grid grid-cols-2 gap-3">
              <div v-for="item in [
                {label:'姓名', value: resumeDetail.name},
                {label:'邮箱', value: resumeDetail.email},
                {label:'电话', value: resumeDetail.phone},
                {label:'城市', value: resumeDetail.location},
                {label:'工作年限', value: resumeDetail.total_years_exp != null ? resumeDetail.total_years_exp + ' 年' : null},
              ].filter(i => i.value)" :key="item.label"
                   class="rounded-lg px-3 py-2" style="background:#f4f6fb;">
                <p class="text-xs" style="font-family:'Inter',sans-serif;color:#757682;">{{ item.label }}</p>
                <p class="text-sm font-semibold" style="font-family:'Inter',sans-serif;color:#0b1c30;">{{ item.value }}</p>
              </div>
            </div>
          </div>
          <!-- Summary - 查看模式 -->
          <div v-if="!isEditing && resumeDetail.summary">
            <p class="text-xs font-semibold tracking-widest uppercase mb-2" style="font-family:'JetBrains Mono',monospace;color:#444651;">个人简介</p>
            <p class="text-sm leading-relaxed" style="font-family:'Inter',sans-serif;color:#374151;">{{ resumeDetail.summary }}</p>
          </div>

          <!-- 编辑模式表单 -->
          <div v-if="isEditing" class="flex flex-col gap-3">
            <p class="text-xs font-semibold tracking-widest uppercase mb-1" style="font-family:'JetBrains Mono',monospace;color:#444651;">编辑基本信息</p>
            <div class="grid grid-cols-2 gap-3">
              <div v-for="field in [
                {label:'姓名', key:'name', type:'text'},
                {label:'邮箱', key:'email', type:'email'},
                {label:'电话', key:'phone', type:'text'},
                {label:'城市', key:'location', type:'text'},
                {label:'工作年限（年）', key:'total_years_exp', type:'number'},
              ]" :key="field.key" class="flex flex-col gap-1">
                <label class="text-xs" style="font-family:'Inter',sans-serif;color:#757682;">{{ field.label }}</label>
                <input
                  v-model="editForm[field.key as keyof EditForm]"
                  :type="field.type"
                  :placeholder="field.label"
                  class="rounded-lg px-3 py-2 text-sm w-full outline-none"
                  style="background:#f4f6fb;border:1px solid #e0e0ea;font-family:'Inter',sans-serif;color:#0b1c30;"
                  onfocus="this.style.borderColor='#00236f'"
                  onblur="this.style.borderColor='#e0e0ea'"
                />
              </div>
            </div>
            <div class="flex flex-col gap-1">
              <label class="text-xs" style="font-family:'Inter',sans-serif;color:#757682;">个人简介</label>
              <textarea
                v-model="editForm.summary"
                rows="4"
                placeholder="个人简介"
                class="rounded-lg px-3 py-2 text-sm w-full outline-none resize-none"
                style="background:#f4f6fb;border:1px solid #e0e0ea;font-family:'Inter',sans-serif;color:#0b1c30;line-height:1.6;"
                onfocus="this.style.borderColor='#00236f'"
                onblur="this.style.borderColor='#e0e0ea'"
              ></textarea>
            </div>
            <p v-if="resumeModalError" class="text-xs" style="color:#ba1a1a;font-family:'Inter',sans-serif;">{{ resumeModalError }}</p>
          </div>
          <!-- Skills 查看 -->
          <div v-if="!isEditing && resumeDetail.skills?.length">
            <p class="text-xs font-semibold tracking-widest uppercase mb-2" style="font-family:'JetBrains Mono',monospace;color:#444651;">技能</p>
            <div class="flex flex-wrap gap-2">
              <span v-for="skill in resumeDetail.skills" :key="skill"
                    class="px-2 py-1 rounded-full text-xs font-semibold"
                    style="background:#dce9ff;color:#00236f;font-family:'Inter',sans-serif;">{{ skill }}</span>
            </div>
          </div>
          <!-- Skills 编辑 -->
          <div v-if="isEditing">
            <p class="text-xs font-semibold tracking-widest uppercase mb-2" style="font-family:'JetBrains Mono',monospace;color:#444651;">技能</p>
            <div class="flex flex-wrap gap-2 mb-2">
              <span v-for="(skill, idx) in editSkills" :key="skill"
                    class="flex items-center gap-1 pl-2 pr-1 py-1 rounded-full text-xs font-semibold"
                    style="background:#dce9ff;color:#00236f;font-family:'Inter',sans-serif;">
                {{ skill }}
                <button @click="removeSkill(idx)"
                        style="background:none;border:none;cursor:pointer;color:#00236f;padding:0;line-height:1;display:flex;align-items:center;">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:13px;height:13px;">
                    <path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                  </svg>
                </button>
              </span>
            </div>
            <div class="flex gap-2">
              <input v-model="newSkillInput"
                     placeholder="输入技能后按回车或点添加"
                     class="flex-1 rounded-lg px-3 py-1.5 text-sm outline-none"
                     style="background:#f4f6fb;border:1px solid #e0e0ea;font-family:'Inter',sans-serif;"
                     @keydown.enter.prevent="addSkill"
                     onfocus="this.style.borderColor='#00236f'"
                     onblur="this.style.borderColor='#e0e0ea'" />
              <button @click="addSkill"
                      class="px-3 py-1.5 rounded-lg text-xs font-semibold"
                      style="background:#dce9ff;color:#00236f;border:none;cursor:pointer;font-family:'Inter',sans-serif;white-space:nowrap;">
                + 添加
              </button>
            </div>
          </div>
          <!-- Work Experiences -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <p class="text-xs font-semibold tracking-widest uppercase" style="font-family:'JetBrains Mono',monospace;color:#444651;">工作经历</p>
              <button @click="startAddWorkExp" style="background:none;border:none;cursor:pointer;color:#00236f;font-size:12px;font-family:'Inter',sans-serif;display:flex;align-items:center;gap:3px;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg> 添加
              </button>
            </div>
            <div class="flex flex-col gap-3">
              <template v-for="w in resumeDetail.work_experiences" :key="w.id">
                <!-- 编辑表单 -->
                <div v-if="editingWorkExpId === w.id" class="rounded-lg p-4 flex flex-col gap-2" style="background:#f0f4ff;border:1px solid #c7d9ff;">
                  <div class="grid grid-cols-2 gap-2">
                    <div><label class="text-xs" style="color:#757682;">公司 *</label><input v-model="workExpForm.company" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                    <div><label class="text-xs" style="color:#757682;">职位</label><input v-model="workExpForm.title" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                    <div><label class="text-xs" style="color:#757682;">开始时间</label><input v-model="workExpForm.start_date" type="month" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                    <div><label class="text-xs" style="color:#757682;">结束时间（至今留空）</label><input v-model="workExpForm.end_date" type="month" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  </div>
                  <div><label class="text-xs" style="color:#757682;">工作描述</label><textarea v-model="workExpForm.description" rows="3" class="w-full rounded px-2 py-1 text-sm outline-none mt-1 resize-none" style="background:#fff;border:1px solid #d0d5e8;"></textarea></div>
                  <div><label class="text-xs" style="color:#757682;">技术栈（逗号分隔）</label><input v-model="workExpForm.tech_stack" placeholder="Vue, FastAPI, MySQL" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  <div class="flex gap-2 justify-end">
                    <button @click="editingWorkExpId = null" class="px-3 py-1 rounded text-xs" style="background:#f0f0f5;border:none;cursor:pointer;color:#444651;">取消</button>
                    <button @click="saveWorkExp" :disabled="savingWorkExp" class="px-3 py-1 rounded text-xs" style="background:#00236f;border:none;cursor:pointer;color:#fff;">{{ savingWorkExp ? '保存中...' : '保存' }}</button>
                  </div>
                </div>
                <!-- 查看卡片 -->
                <div v-else class="rounded-lg p-4" style="background:#f4f6fb;">
                  <div class="flex items-start justify-between gap-2 mb-1">
                    <p class="font-semibold text-sm" style="font-family:'Inter',sans-serif;color:#0b1c30;">{{ w.company }}</p>
                    <div class="flex items-center gap-2 flex-shrink-0">
                      <p class="text-xs" style="font-family:'JetBrains Mono',monospace;color:#757682;">{{ w.start_date }}{{ w.end_date ? ' – ' + w.end_date : ' – 至今' }}</p>
                      <button @click="startEditWorkExp(w)" style="background:none;border:none;cursor:pointer;color:#00236f;padding:0;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg></button>
                      <button @click="deleteWorkExp(w.id!)" style="background:none;border:none;cursor:pointer;color:#ba1a1a;padding:0;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg></button>
                    </div>
                  </div>
                  <p v-if="w.title" class="text-xs mb-2" style="font-family:'Inter',sans-serif;color:#444651;">{{ w.title }}</p>
                  <p v-if="w.description" class="text-xs leading-relaxed mb-2" style="font-family:'Inter',sans-serif;color:#6b7280;white-space:pre-wrap;">{{ w.description }}</p>
                  <div v-if="w.tech_stack?.length" class="flex flex-wrap gap-1">
                    <span v-for="t in w.tech_stack" :key="t" class="px-2 py-0.5 rounded text-xs" style="background:#e1e0ff;color:#0d0097;">{{ t }}</span>
                  </div>
                </div>
              </template>
              <!-- 新增表单 -->
              <div v-if="editingWorkExpId === 'new'" class="rounded-lg p-4 flex flex-col gap-2" style="background:#f0f4ff;border:1px solid #c7d9ff;">
                <div class="grid grid-cols-2 gap-2">
                  <div><label class="text-xs" style="color:#757682;">公司 *</label><input v-model="workExpForm.company" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  <div><label class="text-xs" style="color:#757682;">职位</label><input v-model="workExpForm.title" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  <div><label class="text-xs" style="color:#757682;">开始时间</label><input v-model="workExpForm.start_date" placeholder="2023-01" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  <div><label class="text-xs" style="color:#757682;">结束时间</label><input v-model="workExpForm.end_date" placeholder="至今留空" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                </div>
                <div><label class="text-xs" style="color:#757682;">工作描述</label><textarea v-model="workExpForm.description" rows="3" class="w-full rounded px-2 py-1 text-sm outline-none mt-1 resize-none" style="background:#fff;border:1px solid #d0d5e8;"></textarea></div>
                <div><label class="text-xs" style="color:#757682;">技术栈（逗号分隔）</label><input v-model="workExpForm.tech_stack" placeholder="Vue, FastAPI, MySQL" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                <div class="flex gap-2 justify-end">
                  <button @click="editingWorkExpId = null" class="px-3 py-1 rounded text-xs" style="background:#f0f0f5;border:none;cursor:pointer;color:#444651;">取消</button>
                  <button @click="saveWorkExp" :disabled="savingWorkExp" class="px-3 py-1 rounded text-xs" style="background:#00236f;border:none;cursor:pointer;color:#fff;">{{ savingWorkExp ? '保存中...' : '保存' }}</button>
                </div>
              </div>
            </div>
          </div>
          <!-- Projects -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <p class="text-xs font-semibold tracking-widest uppercase" style="font-family:'JetBrains Mono',monospace;color:#444651;">项目经历</p>
              <button v-if="isEditing" @click="startAddProject" style="background:none;border:none;cursor:pointer;color:#00236f;font-size:12px;font-family:'Inter',sans-serif;display:flex;align-items:center;gap:3px;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg> 添加
              </button>
            </div>
            <div class="flex flex-col gap-3">
              <template v-for="p in resumeDetail.projects" :key="p.id">
                <!-- 编辑表单（仅 isEditing 时可触发） -->
                <div v-if="editingProjectId === p.id" class="rounded-lg p-4 flex flex-col gap-2" style="background:#f0f4ff;border:1px solid #c7d9ff;">
                  <div class="grid grid-cols-2 gap-2">
                    <div><label class="text-xs" style="color:#757682;">项目名称 *</label><input v-model="projectForm.name" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                    <div><label class="text-xs" style="color:#757682;">担任角色</label><input v-model="projectForm.role" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                    <div><label class="text-xs" style="color:#757682;">开始时间</label><input v-model="projectForm.start_date" type="month" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                    <div><label class="text-xs" style="color:#757682;">结束时间（至今留空）</label><input v-model="projectForm.end_date" type="month" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  </div>
                  <div><label class="text-xs" style="color:#757682;">项目描述</label><textarea v-model="projectForm.description" rows="10" class="w-full rounded px-2 py-1 text-sm outline-none mt-1 resize-none" style="background:#fff;border:1px solid #d0d5e8;"></textarea></div>
                  <div><label class="text-xs" style="color:#757682;">技术栈（逗号分隔）</label><input v-model="projectForm.tech_stack" placeholder="Vue, FastAPI, MySQL" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  <div class="flex gap-2 justify-end">
                    <button @click="editingProjectId = null" class="px-3 py-1 rounded text-xs" style="background:#f0f0f5;border:none;cursor:pointer;color:#444651;">取消</button>
                    <button @click="saveProject" :disabled="savingProject" class="px-3 py-1 rounded text-xs" style="background:#00236f;border:none;cursor:pointer;color:#fff;">{{ savingProject ? '保存中...' : '保存' }}</button>
                  </div>
                </div>
                <!-- 查看卡片 -->
                <div v-else class="rounded-lg p-4" style="background:#f4f6fb;">
                  <div class="flex items-start justify-between gap-2 mb-1">
                    <p class="font-semibold text-sm" style="font-family:'Inter',sans-serif;color:#0b1c30;">{{ p.name }}</p>
                    <div class="flex items-center gap-2 flex-shrink-0">
                      <p class="text-xs" style="font-family:'JetBrains Mono',monospace;color:#757682;">{{ p.start_date }}{{ p.end_date ? ' – ' + p.end_date : p.start_date ? ' – 至今' : '' }}</p>
                      <template v-if="isEditing">
                        <button @click="startEditProject(p)" style="background:none;border:none;cursor:pointer;color:#00236f;padding:0;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg></button>
                        <button @click="deleteProject(p.id!)" style="background:none;border:none;cursor:pointer;color:#ba1a1a;padding:0;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg></button>
                      </template>
                    </div>
                  </div>
                  <p v-if="p.role" class="text-xs mb-2" style="font-family:'Inter',sans-serif;color:#444651;">{{ p.role }}</p>
                  <p v-if="p.description" class="text-xs leading-relaxed mb-2" style="font-family:'Inter',sans-serif;color:#6b7280;white-space:pre-wrap;">{{ p.description }}</p>
                  <div v-if="p.tech_stack?.length" class="flex flex-wrap gap-1">
                    <span v-for="t in p.tech_stack" :key="t" class="px-2 py-0.5 rounded text-xs" style="background:#e1e0ff;color:#0d0097;">{{ t }}</span>
                  </div>
                </div>
              </template>
              <!-- 新增表单 -->
              <div v-if="editingProjectId === 'new'" class="rounded-lg p-4 flex flex-col gap-2" style="background:#f0f4ff;border:1px solid #c7d9ff;">
                <div class="grid grid-cols-2 gap-2">
                  <div><label class="text-xs" style="color:#757682;">项目名称 *</label><input v-model="projectForm.name" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  <div><label class="text-xs" style="color:#757682;">担任角色</label><input v-model="projectForm.role" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  <div><label class="text-xs" style="color:#757682;">开始时间</label><input v-model="projectForm.start_date" type="month" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  <div><label class="text-xs" style="color:#757682;">结束时间（至今留空）</label><input v-model="projectForm.end_date" type="month" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                </div>
                <div><label class="text-xs" style="color:#757682;">项目描述</label><textarea v-model="projectForm.description" rows="5" class="w-full rounded px-2 py-1 text-sm outline-none mt-1 resize-none" style="background:#fff;border:1px solid #d0d5e8;"></textarea></div>
                <div><label class="text-xs" style="color:#757682;">技术栈（逗号分隔）</label><input v-model="projectForm.tech_stack" placeholder="Vue, FastAPI, MySQL" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                <div class="flex gap-2 justify-end">
                  <button @click="editingProjectId = null" class="px-3 py-1 rounded text-xs" style="background:#f0f0f5;border:none;cursor:pointer;color:#444651;">取消</button>
                  <button @click="saveProject" :disabled="savingProject" class="px-3 py-1 rounded text-xs" style="background:#00236f;border:none;cursor:pointer;color:#fff;">{{ savingProject ? '保存中...' : '保存' }}</button>
                </div>
              </div>
            </div>
          </div>
          <!-- Educations -->
          <div>
            <div class="flex items-center justify-between mb-3">
              <p class="text-xs font-semibold tracking-widest uppercase" style="font-family:'JetBrains Mono',monospace;color:#444651;">教育经历</p>
              <button v-if="isEditing" @click="startAddEdu" style="background:none;border:none;cursor:pointer;color:#00236f;font-size:12px;font-family:'Inter',sans-serif;display:flex;align-items:center;gap:3px;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg> 添加
              </button>
            </div>
            <div class="flex flex-col gap-3">
              <template v-for="e in resumeDetail.educations" :key="e.id">
                <!-- 编辑表单 -->
                <div v-if="editingEduId === e.id" class="rounded-lg p-4 flex flex-col gap-2" style="background:#f0f4ff;border:1px solid #c7d9ff;">
                  <div class="grid grid-cols-2 gap-2">
                    <div><label class="text-xs" style="color:#757682;">学校 *</label><input v-model="eduForm.school" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                    <div><label class="text-xs" style="color:#757682;">学历</label><input v-model="eduForm.degree" placeholder="本科/硕士/博士" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                    <div><label class="text-xs" style="color:#757682;">专业</label><input v-model="eduForm.major" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                    <div><label class="text-xs" style="color:#757682;">毕业年份</label><select v-model="eduForm.graduation_year" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;color:#0b1c30;"><option value="">请选择</option><option v-for="y in Array.from({length: 30}, (_, i) => new Date().getFullYear() + 6 - i)" :key="y" :value="String(y)">{{ y }}</option></select></div>
                  </div>
                  <div class="flex gap-2 justify-end">
                    <button @click="editingEduId = null" class="px-3 py-1 rounded text-xs" style="background:#f0f0f5;border:none;cursor:pointer;color:#444651;">取消</button>
                    <button @click="saveEdu" :disabled="savingEdu" class="px-3 py-1 rounded text-xs" style="background:#00236f;border:none;cursor:pointer;color:#fff;">{{ savingEdu ? '保存中...' : '保存' }}</button>
                  </div>
                </div>
                <!-- 查看卡片 -->
                <div v-else class="rounded-lg p-4 flex items-start justify-between gap-2" style="background:#f4f6fb;">
                  <div>
                    <p class="font-semibold text-sm" style="font-family:'Inter',sans-serif;color:#0b1c30;">{{ e.school }}</p>
                    <p class="text-xs mt-1" style="font-family:'Inter',sans-serif;color:#444651;">
                      {{ [e.degree, e.major, e.graduation_year ? e.graduation_year + ' 毕业' : null].filter(Boolean).join(' · ') || '-' }}
                    </p>
                  </div>
                  <div v-if="isEditing" class="flex items-center gap-2 flex-shrink-0">
                    <button @click="startEditEdu(e)" style="background:none;border:none;cursor:pointer;color:#00236f;padding:0;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg></button>
                    <button @click="deleteEdu(e.id!)" style="background:none;border:none;cursor:pointer;color:#ba1a1a;padding:0;"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg></button>
                  </div>
                </div>
              </template>
              <!-- 新增表单 -->
              <div v-if="editingEduId === 'new'" class="rounded-lg p-4 flex flex-col gap-2" style="background:#f0f4ff;border:1px solid #c7d9ff;">
                <div class="grid grid-cols-2 gap-2">
                  <div><label class="text-xs" style="color:#757682;">学校 *</label><input v-model="eduForm.school" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  <div><label class="text-xs" style="color:#757682;">学历</label><input v-model="eduForm.degree" placeholder="本科/硕士/博士" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  <div><label class="text-xs" style="color:#757682;">专业</label><input v-model="eduForm.major" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                  <div><label class="text-xs" style="color:#757682;">毕业年份</label><input v-model="eduForm.graduation_year" placeholder="2024" class="w-full rounded px-2 py-1 text-sm outline-none mt-1" style="background:#fff;border:1px solid #d0d5e8;" /></div>
                </div>
                <div class="flex gap-2 justify-end">
                  <button @click="editingEduId = null" class="px-3 py-1 rounded text-xs" style="background:#f0f0f5;border:none;cursor:pointer;color:#444651;">取消</button>
                  <button @click="saveEdu" :disabled="savingEdu" class="px-3 py-1 rounded text-xs" style="background:#00236f;border:none;cursor:pointer;color:#fff;">{{ savingEdu ? '保存中...' : '保存' }}</button>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Toast Notifications -->
    <div class="fixed bottom-6 right-6 z-[70] flex flex-col gap-2" style="max-width:320px;">
      <transition-group name="toast">
        <div v-for="toast in toasts" :key="toast.id"
             class="flex items-start gap-3 rounded-xl px-4 py-3 shadow-lg"
             :style="toast.type === 'success' ? 'background:#0b1c30;border-left:3px solid #6cf8bb;'
                   : toast.type === 'error'   ? 'background:#0b1c30;border-left:3px solid #ff6b6b;'
                   :                            'background:#0b1c30;border-left:3px solid #90a8ff;'">
          <!-- 图标 -->
          <svg v-if="toast.type === 'success'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#6cf8bb" style="width:16px;height:16px;flex-shrink:0;margin-top:1px;">
            <path d="m9 16.17-4.17-4.17-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
          <svg v-else-if="toast.type === 'error'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ff6b6b" style="width:16px;height:16px;flex-shrink:0;margin-top:1px;">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#90a8ff" style="width:16px;height:16px;flex-shrink:0;margin-top:1px;">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
          </svg>
          <p class="text-xs flex-1 leading-relaxed" style="font-family:'Inter',sans-serif;color:#e8eaf0;">{{ toast.message }}</p>
          <button @click="removeToast(toast.id)" style="background:none;border:none;cursor:pointer;color:#757682;padding:0;flex-shrink:0;line-height:1;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;">
              <path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
      </transition-group>
    </div>

    <!-- Confirm Dialog -->
    <div v-if="confirmDialog.open"
         class="fixed inset-0 z-[60] flex items-center justify-center"
         style="background: rgba(11,28,48,0.45); backdrop-filter: blur(4px);">
      <div class="rounded-2xl w-full mx-6 overflow-hidden"
           style="max-width: 360px; background: #ffffff; box-shadow: 0 24px 64px rgba(11,28,48,0.18);">
        <!-- Icon + Title -->
        <div class="px-6 pt-6 pb-4 flex flex-col items-center text-center gap-3">
          <div class="w-12 h-12 rounded-full flex items-center justify-center" style="background:#fff1f1;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:24px;height:24px;color:#ba1a1a;">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
          </div>
          <h3 class="font-semibold" style="font-family:'Inter',sans-serif;font-size:16px;color:#0b1c30;">{{ confirmDialog.title }}</h3>
          <p class="text-sm" style="font-family:'Inter',sans-serif;color:#6b7280;line-height:1.6;">{{ confirmDialog.message }}</p>
        </div>
        <!-- Buttons -->
        <div class="flex border-t" style="border-color:#f0f0f5;">
          <button @click="onConfirmCancel"
                  class="flex-1 py-4 text-sm font-semibold transition-colors"
                  style="font-family:'Inter',sans-serif;color:#444651;background:none;border:none;cursor:pointer;border-right:1px solid #f0f0f5;"
                  onmouseover="this.style.background='#f8f9ff'"
                  onmouseout="this.style.background='none'">
            取消
          </button>
          <button @click="onConfirmOk"
                  class="flex-1 py-4 text-sm font-semibold transition-colors"
                  style="font-family:'Inter',sans-serif;color:#ba1a1a;background:none;border:none;cursor:pointer;"
                  onmouseover="this.style.background='#fff5f5'"
                  onmouseout="this.style.background='none'">
            确认删除
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Bottom Nav -->
    <nav class="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-2 rounded-t-xl"
         style="background: rgba(248,249,255,0.8); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-top: 1px solid rgba(197,197,211,0.2); box-shadow: 0 -10px 30px rgba(30,58,138,0.05);">
      <RouterLink to="/" class="flex flex-col items-center justify-center py-1 px-4 transition-all" style="color: #444651;">
        <span class="material-symbols-outlined">home</span>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">首页</span>
      </RouterLink>
      <RouterLink to="/interview/setup" class="flex flex-col items-center justify-center py-1 px-4 transition-all" style="color: #444651;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:24px;height:24px;">
          <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-3 11-2-1.99V13c0 .55-.45 1-1 1H8c-.55 0-1-.45-1-1V7c0-.55.45-1 1-1h6c.55 0 1 .45 1 1v1.99L17 7v6z"></path>
        </svg>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">面试</span>
      </RouterLink>
      <RouterLink to="/results" class="flex flex-col items-center justify-center py-1 px-4 transition-all" style="color: #444651;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:24px;height:24px;">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"></path>
          <path d="M7 12h2v5H7zm8-5h2v10h-2zm-4 7h2v3h-2zm0-4h2v2h-2z"></path>
        </svg>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">结果</span>
      </RouterLink>
      <RouterLink to="/profile" class="flex flex-col items-center justify-center py-1 px-4 rounded-full transition-all" style="background-color: #1e3a8a; color: #90a8ff;">
        <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;">settings</span>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">设置</span>
      </RouterLink>
    </nav>

  </div>
</template>

<style scoped>
/* 品牌图标呼吸动画 */
.logo-breathe {
  animation: breathe 2.4s ease-in-out infinite;
}
@keyframes breathe {
  0%, 100% { transform: scale(1);   box-shadow: 0 8px 32px rgba(0,35,111,0.22); }
  50%       { transform: scale(1.08); box-shadow: 0 12px 40px rgba(0,35,111,0.34); }
}

/* 简历解析绕圈动画 */
.resume-orbit {
  animation: orbit-spin 1.2s linear infinite;
  transform-origin: center;
}
@keyframes orbit-spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

/* Toast 通知动画 */
.toast-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toast-leave-active {
  transition: all 0.22s ease-in;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(40px) scale(0.95);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(40px) scale(0.92);
}
.toast-move {
  transition: transform 0.25s ease;
}

/* 三点波浪 */
.dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #00236f;
  animation: wave 1.3s ease-in-out infinite;
}
.dot-1 { animation-delay: 0s;    opacity: 0.35; }
.dot-2 { animation-delay: 0.18s; opacity: 0.35; }
.dot-3 { animation-delay: 0.36s; opacity: 0.35; }
@keyframes wave {
  0%, 70%, 100% { transform: translateY(0);   opacity: 0.35; }
  35%           { transform: translateY(-9px); opacity: 1;    }
}
</style>

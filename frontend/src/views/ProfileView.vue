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

const profileName = computed(() => {
  const username = profileData.value?.username ?? session.value?.username ?? '用户'
  return String(username)
})

const userInitial = computed(() => profileName.value.slice(0, 1).toUpperCase())

const totalPoints = computed(() => {
  const rawValue = profileData.value?.total_points
  return typeof rawValue === 'number' ? rawValue : 0
})

const totalPages = computed(() => Math.max(1, Math.ceil(totalRecordCount.value / PAGE_SIZE)))
const pageStart = computed(() => (totalRecordCount.value === 0 ? 0 : (currentPage.value - 1) * PAGE_SIZE + 1))
const pageEnd = computed(() => Math.min(currentPage.value * PAGE_SIZE, totalRecordCount.value))

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

  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function goHome() {
  router.push('/')
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
    await loadPointRecords()
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

    <!-- TopAppBar -->
    <header class="fixed top-0 z-50 w-full h-16 flex justify-between items-center px-6"
            style="background: rgba(248,249,255,0.8); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-bottom: 1px solid rgba(197,197,211,0.2); box-shadow: 0 1px 4px rgba(30,58,138,0.04);">
      <div class="flex items-center gap-3 cursor-pointer" @click="goHome">
        <span class="material-symbols-outlined" style="color: #00236f;">menu</span>
        <h1 class="font-bold text-2xl leading-tight" style="color: #00236f; font-family: 'Inter', sans-serif;">InterviewAI</h1>
      </div>
      <div class="flex items-center gap-6">
        <div class="hidden md:flex gap-6 items-center">
          <RouterLink to="/" class="text-xs font-semibold tracking-widest uppercase transition-colors px-2 py-1 rounded"
                      style="font-family: 'JetBrains Mono', monospace; color: #444651;">首页</RouterLink>
          <RouterLink to="/interview/setup" class="text-xs font-semibold tracking-widest uppercase transition-colors px-2 py-1 rounded"
                      style="font-family: 'JetBrains Mono', monospace; color: #444651;">面试</RouterLink>
          <RouterLink to="/results" class="text-xs font-semibold tracking-widest uppercase transition-colors px-2 py-1 rounded"
                      style="font-family: 'JetBrains Mono', monospace; color: #444651;">结果</RouterLink>
          <RouterLink to="/profile" class="text-xs font-semibold tracking-widest uppercase px-2 py-1 rounded font-bold"
                      style="font-family: 'JetBrains Mono', monospace; color: #00236f;">个人中心</RouterLink>
        </div>
        <div class="w-10 h-10 rounded-full overflow-hidden flex items-center justify-center" style="background-color: #1e3a8a;">
          <span class="font-bold text-sm" style="color: #90a8ff; font-family: 'Inter', sans-serif;">{{ userInitial }}</span>
        </div>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="profileLoading" class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <span class="material-symbols-outlined mb-4 block" style="font-size: 48px; color: #00236f;">hourglass_empty</span>
        <p style="font-family: 'Inter', sans-serif; color: #444651;">正在加载个人中心数据...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="profileError" class="flex items-center justify-center min-h-screen px-6">
      <div class="rounded-xl p-8 text-center max-w-md w-full"
           style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); border-left: 4px solid #ba1a1a; box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
        <span class="material-symbols-outlined mb-4 block" style="font-size: 40px; color: #ba1a1a; font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;">error</span>
        <p class="font-semibold mb-6" style="font-family: 'Inter', sans-serif; color: #0b1c30;">{{ profileError }}</p>
        <button @click="loadProfilePage"
                class="px-6 py-3 rounded-lg font-semibold transition-all active:scale-95"
                style="background-color: #00236f; color: #ffffff; font-family: 'Inter', sans-serif;">
          重新加载
        </button>
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
            <span class="material-symbols-outlined" style="font-size: 18px; color: #ffffff; font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;">verified</span>
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
            <span class="material-symbols-outlined">add_circle</span>
            开始新面试
          </RouterLink>
          <RouterLink to="/results"
                      class="flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all active:scale-95 whitespace-nowrap"
                      style="background: transparent; border: 1px solid #00236f; color: #00236f; font-family: 'Inter', sans-serif; font-size: 16px; line-height: 1;">
            <span class="material-symbols-outlined">history</span>
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
            <span class="material-symbols-outlined" style="font-size: 32px;">video_chat</span>
          </div>
          <div>
            <p class="text-xs font-semibold tracking-widest uppercase mb-1" style="font-family: 'JetBrains Mono', monospace; color: #444651;">总面试次数</p>
            <p class="font-semibold" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #0b1c30;">{{ totalRecordCount }}</p>
          </div>
        </div>

        <!-- Avg Score Card -->
        <div class="rounded-xl p-6 flex items-center gap-6"
             style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
          <div class="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style="background-color: #6cf8bb; color: #006c49;">
            <span class="material-symbols-outlined" style="font-size: 32px;">analytics</span>
          </div>
          <div>
            <p class="text-xs font-semibold tracking-widest uppercase mb-1" style="font-family: 'JetBrains Mono', monospace; color: #444651;">当前积分</p>
            <p class="font-semibold" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #0b1c30;">
              {{ totalPoints }}<span class="font-normal" style="font-size: 24px; line-height: 1.3;"> 分</span>
            </p>
          </div>
        </div>

        <!-- Points Card -->
        <div class="rounded-xl p-6 flex items-center gap-6"
             style="background: rgba(255,255,255,0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3); border: 2px solid rgba(0,35,111,0.1); box-shadow: 0 10px 30px rgba(30,58,138,0.05);">
          <div class="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0" style="background-color: #e1e0ff; color: #0d0097;">
            <span class="material-symbols-outlined" style="font-size: 32px;">military_tech</span>
          </div>
          <div>
            <p class="text-xs font-semibold tracking-widest uppercase mb-1" style="font-family: 'JetBrains Mono', monospace; color: #444651;">积分记录条数</p>
            <p class="font-semibold" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #0b1c30;">{{ displayRecords.length }}</p>
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
              <span class="material-symbols-outlined" style="color: #00236f;">receipt_long</span>
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
                  <span class="material-symbols-outlined" style="color: #00236f; font-size: 20px;">
                    {{ record.sign === 'positive' ? 'add_circle' : record.sign === 'negative' ? 'remove_circle' : 'circle' }}
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
                <span class="material-symbols-outlined" style="color: #757682;">chevron_right</span>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="p-12 text-center">
            <span class="material-symbols-outlined mb-4 block" style="font-size: 48px; color: #c5c5d3;">receipt_long</span>
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
            <span class="material-symbols-outlined" style="color: #00236f;">description</span>
            简历管理
          </h3>
          <div class="rounded-lg p-6 text-center mb-6"
               style="background-color: #ffffff; border: 2px dashed #c5c5d3;">
            <span class="material-symbols-outlined mb-2 block" style="font-size: 40px; color: rgba(0,35,111,0.3);">cloud_upload</span>
            <p class="font-semibold text-sm mb-1" style="font-family: 'Inter', sans-serif; color: #0b1c30;">Standard_Resume_2023.pdf</p>
            <p class="text-xs" style="font-family: 'Inter', sans-serif; color: #444651;">Last uploaded: 2 days ago</p>
          </div>
          <div class="flex flex-col gap-2">
            <button class="w-full py-2 rounded-lg text-sm font-semibold transition-colors"
                    style="background-color: #dce9ff; color: #444651; font-family: 'Inter', sans-serif;"
                    onmouseover="this.style.backgroundColor='#d3e4fe'"
                    onmouseout="this.style.backgroundColor='#dce9ff'">
              替换文件
            </button>
            <button class="w-full py-2 rounded-lg text-sm font-semibold transition-colors"
                    style="background: transparent; color: #00236f; font-family: 'Inter', sans-serif;"
                    onmouseover="this.style.backgroundColor='rgba(0,35,111,0.05)'"
                    onmouseout="this.style.backgroundColor='transparent'">
              查看分析
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
          <span class="material-symbols-outlined">logout</span>
          退出登录
        </button>
      </aside>

    </main>

    <!-- Mobile Bottom Nav -->
    <nav class="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 py-2 rounded-t-xl"
         style="background: rgba(248,249,255,0.8); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-top: 1px solid rgba(197,197,211,0.2); box-shadow: 0 -10px 30px rgba(30,58,138,0.05);">
      <RouterLink to="/" class="flex flex-col items-center justify-center py-1 px-4 transition-all" style="color: #444651;">
        <span class="material-symbols-outlined">home</span>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">首页</span>
      </RouterLink>
      <RouterLink to="/interview/setup" class="flex flex-col items-center justify-center py-1 px-4 transition-all" style="color: #444651;">
        <span class="material-symbols-outlined">video_chat</span>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">面试</span>
      </RouterLink>
      <RouterLink to="/results" class="flex flex-col items-center justify-center py-1 px-4 transition-all" style="color: #444651;">
        <span class="material-symbols-outlined">analytics</span>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">结果</span>
      </RouterLink>
      <RouterLink to="/profile" class="flex flex-col items-center justify-center py-1 px-4 rounded-full transition-all" style="background-color: #1e3a8a; color: #90a8ff;">
        <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;">settings</span>
        <span class="text-xs font-semibold tracking-widest" style="font-family: 'JetBrains Mono', monospace;">设置</span>
      </RouterLink>
    </nav>

  </div>
</template>

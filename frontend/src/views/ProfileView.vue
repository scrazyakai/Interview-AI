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

  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
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
            <p class="font-semibold" style="font-family: 'Inter', sans-serif; font-size: 36px; line-height: 1.2; letter-spacing: -0.01em; color: #0b1c30;">{{ totalRecordCount }}</p>
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
              {{ totalPoints }}<span class="font-normal" style="font-size: 24px; line-height: 1.3;"> 分</span>
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
          <div class="rounded-lg p-6 text-center mb-6"
               style="background-color: #ffffff; border: 2px dashed #c5c5d3;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="mb-2 block mx-auto transition-colors" style="width:40px;height:40px;" :style="{ color: hasResume ? '#006c49' : 'rgba(0,35,111,0.3)' }">
              <path d="M19.35 10.04A7.49 7.49 0 0 0 12 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 0 0 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM19 18H6c-2.21 0-4-1.79-4-4 0-2.05 1.53-3.76 3.56-3.97l1.07-.11.5-.95A5.469 5.469 0 0 1 12 6c2.62 0 4.88 1.86 5.39 4.43l.3 1.5 1.53.11A2.98 2.98 0 0 1 22 15c0 1.65-1.35 3-3 3zM8 13h2.55v3h2.9v-3H16l-4-4z"></path>
            </svg>
            <p v-if="resumeFileName" class="font-semibold text-sm mb-1" style="font-family: 'Inter', sans-serif; color: #0b1c30;">{{ resumeFileName }}</p>
            <p class="text-xs" style="font-family: 'Inter', sans-serif; color: #444651;">{{ hasResume ? 'Resume on file' : 'No resume uploaded yet' }}</p>
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
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:18px;height:18px;flex-shrink:0;">
            <path d="m17 7-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"></path>
          </svg>
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

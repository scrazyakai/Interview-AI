<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppTopbar from '../components/AppTopbar.vue'

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
  const username = profileData.value?.username ?? session.value?.username ?? '\u7528\u6237'
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
    { key: 'username', label: '\u7528\u6237\u540d', value: formatValue(data.username) },
    { key: 'user_id', label: '\u7528\u6237 ID', value: formatValue(data.user_id) },
    { key: 'total_points', label: '\u5f53\u524d\u79ef\u5206', value: `${totalPoints.value} \u5206` },
  ]
})

const displayRecords = computed<DisplayPointRecord[]>(() =>
  pointRecords.value.map((record) => {
    const changePoint = toNumber(record.change_point)

    return {
      item: getRecordItem(record),
      changePoint,
      description: formatText(record.description, '\u6682\u65e0\u8bf4\u660e'),
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
    throw new Error('\u672a\u68c0\u6d4b\u5230\u767b\u5f55\u72b6\u6001\uff0c\u8bf7\u5148\u767b\u5f55\u3002')
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Authorization: `${currentSession.token_type} ${currentSession.access_token}`,
    },
  })

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(getApiErrorMessage(data, '\u8bf7\u6c42\u5931\u8d25\uff0c\u8bf7\u7a0d\u540e\u91cd\u8bd5\u3002'))
  }

  const payload = extractApiPayload<T>(data)
  if (payload === null) {
    throw new Error('\u8bf7\u6c42\u5931\u8d25\uff1a\u670d\u52a1\u54cd\u5e94\u6570\u636e\u683c\u5f0f\u4e0d\u6b63\u786e\u3002')
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
  const item = formatText(record.item, '\u79ef\u5206\u53d8\u52a8')
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
      error instanceof Error ? error.message : '\u52a0\u8f7d\u4e2a\u4eba\u4e2d\u5fc3\u5931\u8d25\u3002'
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
      error instanceof Error ? error.message : '\u52a0\u8f7d\u79ef\u5206\u8bb0\u5f55\u5931\u8d25\u3002'
  } finally {
    profileLoading.value = false
  }
}
</script>

<template>
  <main class="profile-page">
    <section class="profile-shell">
      <AppTopbar :session="session" @logout="logout" />

      <section v-if="profileError" class="profile-error">
        {{ profileError }}
      </section>

      <section v-else-if="profileLoading" class="profile-loading">
        &#27491;&#22312;&#21152;&#36733;&#20010;&#20154;&#20013;&#24515;&#25968;&#25454;...
      </section>

      <template v-else>
        <section class="profile-layout">
          <div class="profile-left">
            <article class="profile-card profile-summary-card">
              <div class="profile-avatar-wrap">
                <img
                  v-if="profileData?.avatar_url"
                  :src="profileData.avatar_url"
                  alt="avatar"
                  class="profile-avatar-image"
                />
                <div v-else class="profile-avatar-fallback">{{ userInitial }}</div>
              </div>

              <h2 class="profile-name">{{ profileName }}</h2>
              <p class="profile-bio">
                &#27426;&#36814;&#22238;&#26469;&#65292;&#36825;&#37324;&#21487;&#20197;&#26597;&#30475;&#20320;&#30340;&#36134;&#25143;&#20449;&#24687;&#21644;&#31215;&#20998;&#21464;&#21270;&#12290;
              </p>

              <div class="profile-detail-list">
                <div v-for="field in profileFields" :key="field.key" class="profile-detail-item">
                  <span class="detail-label">{{ field.label }}</span>
                  <span class="detail-value">{{ field.value }}</span>
                </div>
              </div>
            </article>

            <article class="profile-card points-balance-card">
              <p class="card-kicker">&#24403;&#21069;&#31215;&#20998;</p>
              <div class="points-balance-row">
                <div>
                  <p class="points-balance-value">{{ totalPoints }}</p>
                  <p class="points-balance-unit">&#20998;</p>
                </div>
                <div class="points-balance-note">
                  &#31215;&#20998;&#20250;&#26681;&#25454;&#27880;&#20876;&#36192;&#36865;&#12289;&#28040;&#36153;&#25110;&#20854;&#20182;&#19994;&#21153;&#34892;&#20026;&#23454;&#26102;&#21464;&#21270;&#12290;
                </div>
              </div>
            </article>
          </div>

          <article class="profile-card points-record-card">
            <div class="card-head">
              <div>
                <p class="card-kicker">&#31215;&#20998;&#21464;&#21270;</p>
                <h2>&#31215;&#20998;&#35760;&#24405;</h2>
              </div>
              <span class="record-count">{{ displayRecords.length }} &#26465;</span>
            </div>

            <div v-if="displayRecords.length" class="points-record-table">
              <div class="points-record-header">
                <span>&#20107;&#39033;</span>
                <span>&#31215;&#20998;&#21464;&#21270;</span>
                <span>&#35814;&#32454;&#35828;&#26126;</span>
                <span>&#37329;&#39069;</span>
                <span>&#26102;&#38388;</span>
                <span>&#35746;&#21333;</span>
              </div>

              <article
                v-for="(record, index) in displayRecords"
                :key="`${record.createdAt}-${record.orderNo}-${index}`"
                class="points-record-row"
              >
                <span class="record-item-tag">{{ record.item }}</span>
                <span class="record-change" :class="`record-change-${record.sign}`">
                  {{ formatChangePoint(record.changePoint) }}
                </span>
                <span class="record-description">{{ record.description }}</span>
                <span class="record-meta">{{ record.amount }}</span>
                <span class="record-meta">{{ record.createdAt }}</span>
                <span class="record-meta">{{ record.orderNo }}</span>
              </article>
            </div>

            <div v-else class="empty-state">&#26242;&#26080;&#31215;&#20998;&#35760;&#24405;&#12290;</div>

            <div class="points-record-footer">
              <span class="points-record-total">
                &#24635;&#35745; {{ totalRecordCount }} &#26465;，
                &#24403;&#21069;&#26174;&#31034; {{ pageStart }}-{{ pageEnd }} &#26465;
              </span>

              <div class="points-record-pagination">
                <button
                  class="page-button"
                  type="button"
                  :disabled="currentPage <= 1"
                  @click="goToPage(currentPage - 1)"
                >
                  &#19978;&#19968;&#39029;
                </button>
                <span class="page-indicator">{{ currentPage }} / {{ totalPages }}</span>
                <button
                  class="page-button"
                  type="button"
                  :disabled="currentPage >= totalPages"
                  @click="goToPage(currentPage + 1)"
                >
                  &#19979;&#19968;&#39029;
                </button>
              </div>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>

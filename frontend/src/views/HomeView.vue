<template>
  <main
    class="min-h-screen bg-[radial-gradient(circle_at_top,rgba(255,214,170,0.22),transparent_26%),radial-gradient(circle_at_88%_12%,rgba(255,255,255,0.92),transparent_20%),linear-gradient(180deg,#fffaf5_0%,#f8f4ee_42%,#fbf8f3_100%)] text-stone-950"
  >
    <div class="relative overflow-hidden">
      <div class="pointer-events-none absolute inset-x-0 top-0 h-[620px] bg-[linear-gradient(180deg,rgba(255,255,255,0.72),rgba(255,255,255,0))]"></div>
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(rgba(120,113,108,0.035)_1px,transparent_1px),linear-gradient(90deg,rgba(120,113,108,0.035)_1px,transparent_1px)] bg-[size:84px_84px] opacity-40 [mask-image:linear-gradient(180deg,black,transparent_82%)]"></div>
      <div class="pointer-events-none absolute left-[-10%] top-20 h-72 w-72 rounded-full bg-amber-200/45 blur-3xl"></div>
      <div class="pointer-events-none absolute right-[-8%] top-16 h-72 w-72 rounded-full bg-orange-100/40 blur-3xl"></div>

      <AppTopbar
        :on-home="true"
        @login="openAuthDialog('login')"
        @register="openAuthDialog('register')"
        @logout="logout"
      />

      <section class="relative mx-auto flex w-full max-w-7xl flex-col gap-16 px-4 pb-16 pt-10 sm:px-6 lg:px-8 lg:pb-24 lg:pt-16">
        <div class="grid items-center gap-12 lg:grid-cols-[minmax(0,1.05fr)_430px] lg:gap-16">
          <div class="max-w-3xl">
            <div class="inline-flex items-center gap-2 rounded-full border border-white/80 bg-white/82 px-4 py-2 text-sm font-medium text-stone-600 shadow-[0_10px_30px_rgba(120,113,108,0.07)] backdrop-blur">
              <span class="h-2 w-2 rounded-full bg-amber-500"></span>
              AI 实时模拟面试
            </div>

            <h1 class="mt-6 max-w-4xl text-4xl font-semibold leading-[1.03] tracking-[-0.05em] text-stone-950 sm:text-5xl lg:text-[76px]">
              更从容地开始一次，真正贴近求职场景的模拟面试。
            </h1>

            <p class="mt-6 max-w-2xl text-base leading-8 text-stone-600 sm:text-lg">
              先确认岗位、经验级别与面试模式，再补充岗位描述并创建本次面试。路径足够清楚，开始也足够轻松，让你把注意力留给接下来的表达、思考与回答。
            </p>

            <div class="mt-8 flex flex-col gap-3 sm:flex-row">
              <button
                class="inline-flex min-h-14 items-center justify-center rounded-full bg-stone-950 px-7 text-base font-semibold text-white shadow-[0_22px_52px_rgba(87,83,78,0.22)] transition hover:-translate-y-0.5 hover:bg-stone-800"
                type="button"
                @click="handlePrimaryAction"
              >
                {{ activeUser ? '开始模拟面试' : '登录后开始模拟面试' }}
              </button>
              <button
                class="inline-flex min-h-14 items-center justify-center rounded-full border border-stone-200 bg-white/90 px-7 text-base font-semibold text-stone-700 shadow-[0_10px_24px_rgba(120,113,108,0.06)] backdrop-blur transition hover:border-stone-300 hover:text-stone-950"
                type="button"
                @click="scrollToFeatures"
              >
                查看流程
              </button>
            </div>

            <div class="mt-10 grid gap-4 border-t border-stone-200/80 pt-6 sm:grid-cols-3">
              <div v-for="metric in heroMetrics" :key="metric.label">
                <p class="text-[28px] font-semibold tracking-[-0.04em] text-stone-950">{{ metric.value }}</p>
                <p class="mt-1 text-sm leading-6 text-stone-500">{{ metric.label }}</p>
              </div>
            </div>
          </div>

          <div class="relative">
            <div class="absolute inset-8 rounded-[36px] bg-[radial-gradient(circle_at_top,rgba(251,191,36,0.22),transparent_58%),linear-gradient(135deg,rgba(120,113,108,0.12),rgba(255,255,255,0))] blur-3xl"></div>
            <div class="relative overflow-hidden rounded-[36px] border border-white/85 bg-[linear-gradient(180deg,rgba(255,255,255,0.95),rgba(250,246,240,0.94))] p-6 shadow-[0_28px_90px_rgba(120,113,108,0.12)] backdrop-blur">
              <div class="flex items-start justify-between gap-4 border-b border-stone-200/80 pb-5">
                <div>
                  <p class="text-sm font-medium text-stone-500">面试预览</p>
                  <h2 class="mt-3 text-[28px] font-semibold tracking-[-0.04em] text-stone-950">准备清楚之后，再自然地进入训练状态</h2>
                </div>
                <span class="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">可立即开始</span>
              </div>

              <div class="mt-5 grid gap-4">
                <div class="rounded-[28px] border border-stone-200/80 bg-white/92 p-5">
                  <div class="flex items-center justify-between">
                    <p class="text-sm font-medium text-stone-500">当前配置</p>
                    <p class="text-sm font-medium text-stone-400">3 项已完成</p>
                  </div>
                  <div class="mt-4 flex flex-wrap gap-2">
                    <span class="rounded-full bg-stone-100 px-3 py-2 text-sm font-medium text-stone-700">前端工程师</span>
                    <span class="rounded-full bg-stone-100 px-3 py-2 text-sm font-medium text-stone-700">中级</span>
                    <span class="rounded-full bg-stone-100 px-3 py-2 text-sm font-medium text-stone-700">综合面</span>
                  </div>
                </div>

                <div class="rounded-[28px] bg-stone-900 p-5 text-white shadow-[0_18px_44px_rgba(87,83,78,0.22)]">
                  <div class="flex items-center justify-between">
                    <p class="text-sm font-medium text-stone-300">AI 面试官</p>
                    <span class="rounded-full bg-white/10 px-3 py-1 text-xs text-stone-200">实时追问</span>
                  </div>
                  <p class="mt-4 text-base leading-7 text-stone-100">
                    我们先从你最近的一段项目经历开始。你可以先介绍背景、职责分工，以及你最想重点表达的一次技术决策。
                  </p>
                </div>

                <div class="grid gap-3 sm:grid-cols-2">
                  <div
                    v-for="signal in panelSignals"
                    :key="signal.label"
                    class="rounded-[24px] border border-stone-200/80 bg-stone-50/90 px-4 py-4"
                  >
                    <p class="text-xs uppercase tracking-[0.16em] text-stone-400">{{ signal.label }}</p>
                    <p class="mt-2 text-sm font-medium leading-6 text-stone-700">{{ signal.value }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="grid gap-3 border-y border-stone-200/80 py-4 text-sm text-stone-500 sm:grid-cols-4">
          <div v-for="trust in trustSignals" :key="trust" class="flex items-center gap-2">
            <span class="h-1.5 w-1.5 rounded-full bg-stone-400"></span>
            <span>{{ trust }}</span>
          </div>
        </div>

        <section id="features" class="grid gap-7">
          <div class="max-w-2xl">
            <p class="text-sm font-medium text-stone-500">开始流程</p>
            <h2 class="mt-3 text-3xl font-semibold tracking-[-0.04em] text-stone-950 sm:text-[42px]">
              三步完成准备，把精力留给真正重要的表达与回答。
            </h2>
          </div>

          <div class="grid gap-4 lg:grid-cols-3">
            <article
              v-for="step in steps"
              :key="step.id"
              class="rounded-[30px] border border-white/85 bg-white/88 p-6 shadow-[0_18px_48px_rgba(120,113,108,0.08)] backdrop-blur transition hover:-translate-y-1 hover:shadow-[0_24px_56px_rgba(120,113,108,0.11)]"
            >
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-stone-400">步骤 {{ step.id }}</span>
                <span class="rounded-full bg-stone-100 px-3 py-1 text-xs font-medium text-stone-500">{{ step.tag }}</span>
              </div>
              <h3 class="mt-8 text-[28px] font-semibold tracking-[-0.04em] text-stone-950">{{ step.title }}</h3>
              <p class="mt-4 text-sm leading-7 text-stone-600">{{ step.description }}</p>
            </article>
          </div>
        </section>

        <section class="grid gap-8 lg:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)] lg:items-start">
          <div class="max-w-xl">
            <p class="text-sm font-medium text-stone-500">为什么这样设计</p>
            <h2 class="mt-3 text-3xl font-semibold tracking-[-0.04em] text-stone-950 sm:text-[42px]">
              更少的压力感，更清楚的引导，让开始这一步变得自然。
            </h2>
            <p class="mt-5 text-base leading-8 text-stone-600">
              页面不再强调系统说明，而是用更温和、更可信的方式告诉你接下来会发生什么。你不需要先理解一套复杂流程，只需要安心开始这次练习。
            </p>
          </div>

          <div class="grid gap-4 md:grid-cols-3">
            <article
              v-for="value in valuePoints"
              :key="value.title"
              class="rounded-[30px] border border-white/85 bg-white/88 p-6 shadow-[0_18px_48px_rgba(120,113,108,0.08)] backdrop-blur"
            >
              <div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-stone-950 text-lg font-semibold text-white shadow-[0_14px_30px_rgba(87,83,78,0.16)]">
                {{ value.icon }}
              </div>
              <h3 class="mt-5 text-2xl font-semibold tracking-[-0.03em] text-stone-950">{{ value.title }}</h3>
              <p class="mt-4 text-sm leading-7 text-stone-600">{{ value.description }}</p>
            </article>
          </div>
        </section>

        <section class="grid gap-4 rounded-[36px] border border-white/80 bg-[linear-gradient(135deg,#44403c,#57534e_52%,#78716c)] px-6 py-10 text-white shadow-[0_30px_90px_rgba(87,83,78,0.2)] sm:px-10 lg:px-12 lg:py-12">
          <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div class="max-w-2xl">
              <p class="text-sm font-medium text-stone-200">准备好了就开始</p>
              <h2 class="mt-3 text-3xl font-semibold tracking-[-0.04em] sm:text-[42px]">
                现在进入配置页，开始一轮更从容、更贴近真实场景的模拟面试。
              </h2>
              <p class="mt-4 text-base leading-8 text-stone-200/90">
                选择岗位、确认模式、补充描述，然后直接进入实时语音训练。首页到这里结束，接下来把时间交给练习本身。
              </p>
            </div>
            <button
              class="inline-flex min-h-14 items-center justify-center rounded-full bg-white px-7 text-base font-semibold text-stone-950 transition hover:-translate-y-0.5 hover:bg-stone-100"
              type="button"
              @click="handlePrimaryAction"
            >
              {{ activeUser ? '立即开始模拟面试' : '登录后立即开始' }}
            </button>
          </div>
        </section>
      </section>
    </div>

    <div v-if="authDialogOpen" class="fixed inset-0 z-50 grid place-items-center bg-stone-950/45 px-4 backdrop-blur-sm">
      <section class="relative w-full max-w-md rounded-[32px] border border-white/70 bg-white/95 p-7 shadow-[0_32px_80px_rgba(87,83,78,0.18)]">
        <button
          class="absolute right-4 top-4 inline-flex h-10 w-10 items-center justify-center rounded-full bg-stone-100 text-xl text-stone-500 transition hover:bg-stone-200 hover:text-stone-800"
          type="button"
          @click="closeAuthDialog"
        >
          ×
        </button>

        <p class="inline-flex rounded-full bg-stone-100 px-3 py-1 text-sm font-medium text-stone-600">
          {{ authMode === 'login' ? '登录账号' : '注册账号' }}
        </p>
        <h2 class="mt-5 text-3xl font-semibold tracking-[-0.04em] text-stone-950">{{ authTitle }}</h2>
        <p class="mt-3 text-sm leading-7 text-stone-600">{{ authDescription }}</p>

        <form class="mt-7 space-y-4" @submit.prevent="submitAuthForm">
          <label class="block">
            <span class="mb-2 block text-sm font-medium text-stone-700">用户名</span>
            <input
              v-model.trim="authForm.username"
              class="w-full rounded-2xl border border-stone-200 bg-stone-50 px-4 py-3 text-stone-950 outline-none transition focus:border-stone-400 focus:bg-white"
              type="text"
              minlength="3"
              maxlength="32"
              pattern="[A-Za-z0-9]+"
              placeholder="请输入英文或数字用户名"
            />
          </label>

          <label class="block">
            <span class="mb-2 block text-sm font-medium text-stone-700">密码</span>
            <input
              v-model.trim="authForm.password"
              class="w-full rounded-2xl border border-stone-200 bg-stone-50 px-4 py-3 text-stone-950 outline-none transition focus:border-stone-400 focus:bg-white"
              type="password"
              minlength="3"
              maxlength="128"
              placeholder="请输入密码"
            />
          </label>

          <p v-if="authError" class="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ authError }}</p>
          <p v-if="authSuccess" class="rounded-2xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ authSuccess }}</p>

          <button
            class="inline-flex min-h-12 w-full items-center justify-center rounded-full bg-stone-950 px-5 text-base font-semibold text-white transition hover:bg-stone-800 disabled:cursor-wait disabled:opacity-70"
            type="submit"
            :disabled="authLoading"
          >
            {{ authLoading ? '提交中...' : authSubmitLabel }}
          </button>
        </form>

        <button
          class="mt-4 w-full rounded-full border border-stone-200 bg-white px-5 py-3 text-sm font-semibold text-stone-700 transition hover:border-stone-300 hover:text-stone-950"
          type="button"
          @click="toggleAuthMode"
        >
          {{ authToggleLabel }}
        </button>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import AppTopbar from '../components/AppTopbar.vue'
import {
  API_BASE_URL,
  clearAuthSession,
  loadAuthSession,
  saveAuthSession,
  type TokenResponse,
} from '../utils/auth'

type AuthMode = 'login' | 'register'

const heroMetrics = [
  { value: '3 步', label: '完成配置并进入面试' },
  { value: '实时', label: '语音问答直接开始' },
  { value: '岗位定制', label: '训练更贴近目标职位' },
]

const trustSignals = ['岗位定制上下文', '实时语音问答', '中文统一界面', '登录后立即开始']

const steps = [
  {
    id: '01',
    tag: '岗位与级别',
    title: '确认你的目标岗位',
    description: '选择岗位方向与经验级别，让问题难度和关注点更贴近你当前的求职阶段。',
  },
  {
    id: '02',
    tag: '模式与描述',
    title: '补充本次训练重点',
    description: '选择技术面、行为面或综合面，并填写岗位描述，让面试上下文更完整。',
  },
  {
    id: '03',
    tag: '实时开始',
    title: '创建面试并立即开练',
    description: '完成配置后即可进入实时语音面试页面，直接开始问答、表达与临场训练。',
  },
]

const panelSignals = [
  { label: '面试模式', value: '技术面 / 行为面 / 综合面' },
  { label: '开始方式', value: '创建后直接进入实时语音页面' },
]

const valuePoints = [
  {
    icon: '准',
    title: '更贴近真实岗位',
    description: '先明确岗位、级别与面试模式，再进入问答阶段，训练内容更聚焦，不再像泛泛聊天。',
  },
  {
    icon: '轻',
    title: '开始更轻松自然',
    description: '首页只承担引导与转化，核心操作集中在配置页，减少理解负担，让你更自然地进入练习。',
  },
  {
    icon: '稳',
    title: '实时语音更有沉浸感',
    description: '创建完成后直接进入实时语音面试流程，适合反复练习表达、节奏和回答结构。',
  },
]

const USERNAME_PATTERN = /^[A-Za-z0-9]+$/
const router = useRouter()
const authMode = ref<AuthMode>('login')
const authDialogOpen = ref(false)
const authLoading = ref(false)
const authError = ref('')
const authSuccess = ref('')
const activeUser = ref<TokenResponse | null>(null)
const authForm = ref({ username: '', password: '' })

const authTitle = computed(() => (authMode.value === 'login' ? '登录账号' : '创建账号'))
const authDescription = computed(() =>
  authMode.value === 'login'
    ? '登录后即可创建面试配置并进入实时模拟面试。'
    : '注册成功后会自动保存登录状态，随后就可以开始模拟面试。',
)
const authSubmitLabel = computed(() => (authMode.value === 'login' ? '登录' : '注册'))
const authToggleLabel = computed(() =>
  authMode.value === 'login' ? '没有账号？立即注册' : '已有账号？去登录',
)

function syncSession() {
  activeUser.value = loadAuthSession()
}

function scrollToFeatures() {
  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
}

function openAuthDialog(mode: AuthMode) {
  authMode.value = mode
  authDialogOpen.value = true
  authError.value = ''
  authSuccess.value = ''
}

function closeAuthDialog() {
  authDialogOpen.value = false
  authError.value = ''
  authSuccess.value = ''
}

function toggleAuthMode() {
  authMode.value = authMode.value === 'login' ? 'register' : 'login'
  authError.value = ''
  authSuccess.value = ''
}

function goInterviewSetup() {
  if (!activeUser.value) {
    openAuthDialog('login')
    return
  }

  router.push('/interview/setup')
}

function handlePrimaryAction() {
  goInterviewSetup()
}

function logout() {
  clearAuthSession()
  activeUser.value = null
}

async function submitAuthForm() {
  authError.value = ''
  authSuccess.value = ''

  const username = authForm.value.username.trim()
  const password = authForm.value.password.trim()

  if (username.length < 3 || password.length < 3) {
    authError.value = '用户名和密码至少需要 3 个字符。'
    return
  }

  if (!USERNAME_PATTERN.test(username)) {
    authError.value = '用户名只能包含英文和数字。'
    return
  }

  authLoading.value = true

  try {
    const endpoint = authMode.value === 'login' ? '/auth/login' : '/auth/register'
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })

    const data = (await response.json().catch(() => null)) as
      | TokenResponse
      | { detail?: string; message?: string }
      | null

    if (!response.ok) {
      const errorData = data as { detail?: string; message?: string } | null
      authError.value = errorData?.detail ?? errorData?.message ?? '认证失败，请稍后重试。'
      return
    }

    const session = data as TokenResponse
    saveAuthSession(session)
    syncSession()
    authForm.value.password = ''
    authSuccess.value = authMode.value === 'login' ? '登录成功。' : '注册成功，已自动登录。'

    window.setTimeout(() => {
      closeAuthDialog()
    }, 400)
  } catch (error) {
    authError.value = error instanceof Error ? error.message : '请求认证接口失败。'
  } finally {
    authLoading.value = false
  }
}

onMounted(() => {
  syncSession()
})
</script>

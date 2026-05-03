<template>
  <main class="min-h-screen bg-[#f8f8f6]">
    <div class="px-4 pb-2 pt-4 sm:px-6 lg:px-8">
      <AppTopbar :on-home="true" @login="openAuthDialog('login')" @register="openAuthDialog('register')" @logout="logout" />
    </div>

    <HomePage />

    <div v-if="authDialogOpen" class="fixed inset-0 z-50 grid place-items-center bg-stone-950/45 px-4 backdrop-blur-sm">
      <section class="relative w-full max-w-md rounded-[28px] border border-white/70 bg-white/95 p-7 shadow-[0_32px_80px_rgba(87,83,78,0.18)]">
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

import AppTopbar from '../components/AppTopbar.vue'
import {
  API_BASE_URL,
  clearAuthSession,
  getApiErrorMessage,
  loadAuthSession,
  saveAuthSession,
  type TokenResponse,
} from '../utils/auth'
import HomePage from './HomePage.vue'

type AuthMode = 'login' | 'register'

const USERNAME_PATTERN = /^[A-Za-z0-9]+$/

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

    const data = await response.json().catch(() => null)

    if (!response.ok) {
      authError.value = getApiErrorMessage(data, '认证失败，请稍后重试。')
      return
    }

    saveAuthSession(data)
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

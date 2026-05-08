<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { loadAuthSession, type TokenResponse } from '../utils/auth'

const props = defineProps<{
  onHome?: boolean
}>()

const emit = defineEmits<{
  login: []
  register: []
  logout: []
}>()

const router = useRouter()
const route = useRoute()
const userMenuOpen = ref(false)
const internalSession = ref<TokenResponse | null>(null)

const currentSession = computed(() => internalSession.value)
const userInitial = computed(() => currentSession.value?.username.slice(0, 1).toUpperCase() ?? 'U')
const isHomeRoute = computed(() => route.path === '/')
const isInterviewRoute = computed(() => route.path.startsWith('/interview'))
const isAboutRoute = computed(() => route.path === '/about')

function syncSession() {
  internalSession.value = loadAuthSession()
}

function handleDocumentClick(event: MouseEvent) {
  const target = event.target
  if (!(target instanceof HTMLElement)) return
  if (!target.closest('.user-menu')) {
    userMenuOpen.value = false
  }
}

function toggleUserMenu() {
  userMenuOpen.value = !userMenuOpen.value
}

function goHome() {
  router.push('/')
}

function goInterview() {
  router.push('/interview/setup')
}

function goAbout() {
  router.push('/about')
}

function goProfile() {
  userMenuOpen.value = false
  router.push('/profile')
}

function handleLogin() {
  if (props.onHome) {
    emit('login')
    return
  }

  router.push('/')
}

function handleRegister() {
  if (props.onHome) {
    emit('register')
    return
  }

  router.push('/')
}

function handleLogout() {
  userMenuOpen.value = false
  emit('logout')
}

watch(
  () => route.fullPath,
  () => {
    userMenuOpen.value = false
    syncSession()
  },
)

onMounted(() => {
  syncSession()
  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<template>
  <header class="bg-surface/80 backdrop-blur-md border-b border-outline-variant/20 shadow-sm fixed top-0 left-0 w-full z-50 h-16 flex justify-between items-center px-6">
    <!-- Brand -->
    <button
      type="button"
      class="flex items-center gap-2 cursor-pointer active:scale-95 duration-200"
      @click="goHome"
    >
      <span class="material-symbols-outlined text-primary" style="font-size:24px;">psychology</span>
      <span class="font-bold text-xl text-primary" style="font-family: 'Inter', sans-serif;">InterviewAI</span>
    </button>

    <!-- Desktop Nav -->
    <nav class="hidden md:flex items-center gap-6">
      <button
        type="button"
        class="text-sm transition-colors px-2 py-1 rounded"
        style="font-family: 'Inter', sans-serif;"
        :class="isHomeRoute ? 'font-semibold text-primary' : 'text-on-surface-variant hover:bg-primary-container/10'"
        @click="goHome"
      >首页</button>
      <button
        type="button"
        class="text-sm transition-colors px-2 py-1 rounded"
        style="font-family: 'Inter', sans-serif;"
        :class="isInterviewRoute ? 'font-semibold text-primary' : 'text-on-surface-variant hover:bg-primary-container/10'"
        @click="goInterview"
      >面试</button>
      <button
        type="button"
        class="text-sm transition-colors px-2 py-1 rounded"
        style="font-family: 'Inter', sans-serif;"
        :class="isAboutRoute ? 'font-semibold text-primary' : 'text-on-surface-variant hover:bg-primary-container/10'"
        @click="goAbout"
      >结果</button>
    </nav>

    <!-- Right: User area -->
    <div class="flex items-center gap-3">
      <template v-if="currentSession">
        <div class="user-menu relative">
          <button
            type="button"
            class="flex items-center gap-2 rounded-full border border-outline-variant/30 bg-surface-container-low px-3 py-1.5 text-sm font-semibold text-on-surface shadow-sm transition-all hover:bg-surface-container-high active:scale-95"
            style="font-family: 'Inter', sans-serif;"
            @click.stop="toggleUserMenu"
          >
            <span
              class="flex h-7 w-7 items-center justify-center rounded-full bg-primary text-xs font-bold text-on-primary"
            >{{ userInitial }}</span>
            <span class="hidden sm:block max-w-[120px] truncate">{{ currentSession.username }}</span>
            <span class="material-symbols-outlined text-outline transition-transform duration-200" style="font-size:18px;" :class="{ 'rotate-180': userMenuOpen }">expand_more</span>
          </button>

          <!-- Dropdown -->
          <div
            v-if="userMenuOpen"
            class="absolute right-0 top-full mt-2 w-52 rounded-xl border border-outline-variant/20 bg-surface/95 shadow-[0_10px_30px_rgba(30,58,138,0.12)] backdrop-blur-xl z-50"
          >
            <div class="px-4 pt-3 pb-2">
              <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.15em] text-on-surface-variant">已登录账号</p>
              <p class="mt-0.5 truncate text-sm font-semibold text-on-surface">{{ currentSession.username }}</p>
            </div>
            <div class="mx-3 border-t border-outline-variant/20"></div>
            <div class="p-1.5">
              <button
                type="button"
                class="flex w-full flex-col rounded-lg px-3 py-2 text-left transition-colors hover:bg-surface-container-low"
                @click="goProfile"
              >
                <span class="text-sm font-semibold text-on-surface">个人中心</span>
                <span class="text-xs text-on-surface-variant">查看资料与积分记录</span>
              </button>
              <button
                type="button"
                class="flex w-full flex-col rounded-lg px-3 py-2 text-left transition-colors hover:bg-error-container/40"
                @click="handleLogout"
              >
                <span class="text-sm font-semibold text-error">退出登录</span>
                <span class="text-xs text-on-surface-variant">结束当前会话</span>
              </button>
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <button
          type="button"
          class="hidden md:inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold transition-all border border-primary text-primary bg-transparent hover:bg-primary/5"
          style="font-family: 'Inter', sans-serif;"
          @click="handleLogin"
        >登录</button>
        <button
          type="button"
          class="inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold transition-all bg-primary text-on-primary hover:opacity-90 active:scale-95"
          style="font-family: 'Inter', sans-serif;"
          @click="handleRegister"
        >立即注册</button>
      </template>
    </div>
  </header>
</template>

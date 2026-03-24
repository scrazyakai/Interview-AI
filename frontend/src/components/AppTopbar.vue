<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { loadAuthSession, type TokenResponse } from '../utils/auth'

const props = defineProps<{
  session?: TokenResponse | null
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

const currentSession = computed(() => props.session ?? internalSession.value)
const userInitial = computed(() => currentSession.value?.username.slice(0, 1).toUpperCase() ?? 'U')
const isHomeRoute = computed(() => route.path === '/')
const isInterviewRoute = computed(() => route.path.startsWith('/interview'))

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
  () => props.session,
  (value) => {
    if (value !== undefined) {
      internalSession.value = value
    }
  },
  { immediate: true },
)

watch(
  () => route.fullPath,
  () => {
    userMenuOpen.value = false
    if (props.session === undefined) {
      syncSession()
    }
  },
)

onMounted(() => {
  if (props.session === undefined) {
    syncSession()
  }

  document.addEventListener('click', handleDocumentClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>

<template>
  <header class="topbar-wrap">
    <div class="topbar">
      <button class="brand brand-button" type="button" @click="goHome">
        <div class="brand-mark">M</div>
        <div>
          <p class="brand-name">&#38754;&#35797;&#36215;&#36305;&#32447;</p>
          <p class="brand-subtitle">AI Interview Training</p>
        </div>
      </button>

      <nav class="nav">
        <button class="nav-link" :class="{ 'nav-link-active': isHomeRoute }" type="button" @click="goHome">
          &#39318;&#39029;
        </button>
        <button
          class="nav-link"
          :class="{ 'nav-link-active': isInterviewRoute }"
          type="button"
          @click="goInterview"
        >
          &#27169;&#25311;&#38754;&#35797;
        </button>
        <button class="nav-link" type="button" @click="goHome">&#31616;&#21382;&#35786;&#26029;</button>
      </nav>

      <div class="topbar-actions">
        <template v-if="currentSession">
          <div class="user-menu">
            <button class="avatar-button" type="button" @click.stop="toggleUserMenu">
              <span class="avatar-circle">{{ userInitial }}</span>
              <span class="avatar-name">{{ currentSession.username }}</span>
              <span class="avatar-caret">&#9662;</span>
            </button>

            <div v-if="userMenuOpen" class="user-dropdown">
              <button class="dropdown-item" type="button" @click="goProfile">
                &#20010;&#20154;&#20013;&#24515;
              </button>
              <button class="dropdown-item dropdown-item-danger" type="button" @click="handleLogout">
                &#36864;&#20986;&#30331;&#24405;
              </button>
            </div>
          </div>
        </template>
        <template v-else>
          <button class="ghost-link ghost-button" type="button" @click="handleLogin">
            &#30331;&#24405;
          </button>
          <button class="primary-link" type="button" @click="handleRegister">
            &#31435;&#21363;&#27880;&#20876;
          </button>
        </template>
      </div>
    </div>
  </header>
</template>


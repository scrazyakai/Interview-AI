<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { clearAuthSession, loadAuthSession, type TokenResponse } from '../utils/auth'
import LoginModal from './LoginModal.vue'
import RegisterModal from './RegisterModal.vue'

const router = useRouter()
const route = useRoute()

const session = ref<TokenResponse | null>(loadAuthSession())
const isAdmin = computed(() => session.value?.role === 3)
const showLoginModal = ref(false)
const showRegisterModal = ref(false)
const dropdownVisible = ref(false)
let hideTimer: ReturnType<typeof setTimeout> | null = null

function syncSession() {
  session.value = loadAuthSession()
}

function onLoginSuccess() {
  session.value = loadAuthSession()
}

function onRegisterSuccess() {
  session.value = loadAuthSession()
}

function showDropdown() {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
  dropdownVisible.value = true
}

function scheduleHide() {
  hideTimer = setTimeout(() => {
    dropdownVisible.value = false
  }, 150)
}

function handleLogout() {
  dropdownVisible.value = false
  clearAuthSession()
  session.value = null
  router.push('/')
}

function goProfile() {
  dropdownVisible.value = false
  router.push('/profile')
}

function goAdmin() {
  dropdownVisible.value = false
  router.push('/admin')
}

onMounted(() => {
  syncSession()
})

onUnmounted(() => {
  if (hideTimer) clearTimeout(hideTimer)
})
</script>

<template>
  <header
    style="
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 64px;
      z-index: 50;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 24px;
      box-sizing: border-box;
      background: rgba(248,249,255,0.85);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid rgba(197,197,211,0.2);
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    "
  >
    <div style="display: flex; align-items: center; gap: 8px;">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="currentColor"
        style="width:20px;height:20px;color:#00236f;transform:matrix(-1,0,0,1,0,0);"
      >
        <path d="M13 8.57a1.43 1.43 0 1 0 0 2.86 1.43 1.43 0 0 0 0-2.86z"/>
        <path d="M13 3C9.25 3 6.2 5.94 6.02 9.64L4.1 12.2a.5.5 0 0 0 .4.8H6v3c0 1.1.9 2 2 2h1v3h7v-4.68A6.999 6.999 0 0 0 13 3zm3 7c0 .13-.01.26-.02.39l.83.66c.08.06.1.16.05.25l-.8 1.39c-.05.09-.16.12-.24.09l-.99-.4c-.21.16-.43.29-.67.39L14 13.83c-.01.1-.1.17-.2.17h-1.6c-.1 0-.18-.07-.2-.17l-.15-1.06c-.25-.1-.47-.23-.68-.39l-.99.4c-.09.03-.2 0-.25-.09l-.8-1.39a.19.19 0 0 1 .05-.25l.84-.66c-.01-.13-.02-.26-.02-.39s.02-.27.04-.39l-.85-.66c-.08-.06-.1-.16-.05-.26l.8-1.38c.05-.09.15-.12.24-.09l1 .4c.2-.15.43-.29.67-.39L12 6.17c.02-.1.1-.17.2-.17h1.6c.1 0 .18.07.2.17l.15 1.06c.24.1.46.23.67.39l1-.4c.09-.03.2 0 .24.09l.8 1.38a.2.2 0 0 1-.05.26l-.85.66c.03.12.04.25.04.39z"/>
      </svg>
      <RouterLink
        to="/"
        style="font-weight:700;font-size:20px;color:#00236f;text-decoration:none;font-family:'Inter',sans-serif;"
      >InterviewAI</RouterLink>
    </div>

    <nav style="display: flex; align-items: center; gap: 24px;">
      <RouterLink
        to="/"
        style="font-size:14px;text-decoration:none;font-family:'Inter',sans-serif;transition:color 0.15s;"
        :style="{
          color: route.path === '/' ? '#00236f' : '#444651',
          fontWeight: route.path === '/' ? '600' : '400',
        }"
      >首页</RouterLink>
      <RouterLink
        to="/interview/setup"
        style="font-size:14px;text-decoration:none;font-family:'Inter',sans-serif;transition:color 0.15s;"
        :style="{
          color: route.path.startsWith('/interview') ? '#00236f' : '#444651',
          fontWeight: route.path.startsWith('/interview') ? '600' : '400',
        }"
      >面试</RouterLink>
    </nav>

    <div style="display: flex; align-items: center; gap: 12px;">
      <template v-if="!session">
        <button
          type="button"
          style="
            display: inline-flex;
            align-items: center;
            padding: 7px 18px;
            border-radius: 8px;
            border: 1px solid #00236f;
            background: transparent;
            color: #00236f;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            cursor: pointer;
            transition: background 0.15s;
          "
          @click="showLoginModal = true"
          @mouseenter="($event.currentTarget as HTMLElement).style.background='rgba(0,35,111,0.05)'"
          @mouseleave="($event.currentTarget as HTMLElement).style.background='transparent'"
        >登录</button>
        <button
          type="button"
          style="
            display: inline-flex;
            align-items: center;
            padding: 7px 18px;
            border-radius: 8px;
            background: #00236f;
            color: #ffffff;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            border: none;
            cursor: pointer;
          "
          @click="showRegisterModal = true"
          @mouseenter="($event.currentTarget as HTMLElement).style.background='#001a52'"
          @mouseleave="($event.currentTarget as HTMLElement).style.background='#00236f'"
        >免费开始</button>
      </template>

      <template v-else>
        <div
          style="position: relative; display: flex; align-items: center;"
          @mouseenter="showDropdown"
          @mouseleave="scheduleHide"
        >
          <div
            style="
              display: flex;
              align-items: center;
              gap: 8px;
              padding: 6px 16px;
              border-radius: 999px;
              border: 1px solid rgba(197,197,211,0.5);
              background: transparent;
              cursor: default;
              user-select: none;
            "
          >
            <span style="font-size:18px;line-height:1;">👤</span>
            <span style="font-size:14px;font-weight:600;color:#00236f;font-family:'Inter',sans-serif;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
              {{ session.username }}
            </span>
            <svg
              viewBox="0 0 24 24"
              fill="none"
              style="width:14px;height:14px;color:#444651;transition:transform 0.2s;"
              :style="{ transform: dropdownVisible ? 'rotate(180deg)' : 'rotate(0deg)' }"
            >
              <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>

          <div
            v-if="dropdownVisible"
            style="
              position: absolute;
              right: 0;
              top: calc(100% + 6px);
              width: 180px;
              border-radius: 12px;
              border: 1px solid rgba(197,197,211,0.25);
              background: rgba(248,249,255,0.98);
              box-shadow: 0 8px 24px rgba(30,58,138,0.12);
              backdrop-filter: blur(16px);
              -webkit-backdrop-filter: blur(16px);
              overflow: hidden;
              z-index: 200;
            "
            @mouseenter="showDropdown"
            @mouseleave="scheduleHide"
          >
            <button
              type="button"
              style="
                display: flex;
                align-items: center;
                gap: 10px;
                width: 100%;
                box-sizing: border-box;
                padding: 11px 16px;
                border: none;
                background: transparent;
                text-align: left;
                cursor: pointer;
                font-family: 'Inter', sans-serif;
                transition: background 0.12s;
              "
              @mouseenter="($event.currentTarget as HTMLElement).style.background='rgba(0,35,111,0.06)'"
              @mouseleave="($event.currentTarget as HTMLElement).style.background='transparent'"
              @click="goProfile"
            >
              <svg viewBox="0 0 24 24" fill="currentColor" style="width:16px;height:16px;color:#00236f;flex-shrink:0;">
                <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
              </svg>
              <span style="font-size:14px;font-weight:600;color:#0b1c30;">个人中心</span>
            </button>

            <!-- 管理后台入口：仅 role=3 可见 -->
            <template v-if="isAdmin">
              <div style="margin: 0 12px; border-top: 1px solid rgba(197,197,211,0.2);"></div>
              <button
                type="button"
                style="
                  display: flex;
                  align-items: center;
                  gap: 10px;
                  width: 100%;
                  box-sizing: border-box;
                  padding: 11px 16px;
                  border: none;
                  background: transparent;
                  text-align: left;
                  cursor: pointer;
                  font-family: 'Inter', sans-serif;
                  transition: background 0.12s;
                "
                @mouseenter="($event.currentTarget as HTMLElement).style.background='rgba(124,58,237,0.07)'"
                @mouseleave="($event.currentTarget as HTMLElement).style.background='transparent'"
                @click="goAdmin"
              >
                <svg viewBox="0 0 24 24" fill="currentColor" style="width:16px;height:16px;color:#7c3aed;flex-shrink:0;">
                  <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-1 14H9V9h2v6zm4 0h-2V9h2v6z"/>
                </svg>
                <span style="font-size:14px;font-weight:600;color:#7c3aed;">管理后台</span>
              </button>
            </template>

            <div style="margin: 0 12px; border-top: 1px solid rgba(197,197,211,0.2);"></div>

            <button
              type="button"
              style="
                display: flex;
                align-items: center;
                gap: 10px;
                width: 100%;
                box-sizing: border-box;
                padding: 11px 16px;
                border: none;
                background: transparent;
                text-align: left;
                cursor: pointer;
                font-family: 'Inter', sans-serif;
                transition: background 0.12s;
              "
              @mouseenter="($event.currentTarget as HTMLElement).style.background='rgba(216,30,6,0.06)'"
              @mouseleave="($event.currentTarget as HTMLElement).style.background='transparent'"
              @click="handleLogout"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:16px;height:16px;color:#d81e06;flex-shrink:0;">
                <path d="m17 7-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"></path>
              </svg>
              <span style="font-size:14px;font-weight:600;color:#d81e06;">退出登录</span>
            </button>
          </div>
        </div>
      </template>
    </div>
  </header>

  <LoginModal
    v-if="showLoginModal"
    @close="showLoginModal = false"
    @success="onLoginSuccess"
    @switch-to-register="showLoginModal = false; showRegisterModal = true"
  />

  <RegisterModal
    v-if="showRegisterModal"
    @close="showRegisterModal = false"
    @success="onRegisterSuccess"
    @switch-to-login="showRegisterModal = false; showLoginModal = true"
  />
</template>

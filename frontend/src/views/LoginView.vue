<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { API_BASE_URL, getApiErrorMessage, saveAuthSession } from '../utils/auth'

const router = useRouter()
const route = useRoute()

const mode = ref<'login' | 'register'>('login')

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

function switchMode(target: 'login' | 'register') {
  mode.value = target
  errorMsg.value = ''
  username.value = ''
  password.value = ''
}

function redirectAfterAuth() {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
  router.push(redirect)
}

async function handleLogin() {
  if (!username.value.trim() || !password.value.trim()) {
    errorMsg.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value.trim(), password: password.value.trim() }),
    })

    const data = await res.json().catch(() => null)

    if (!res.ok) {
      errorMsg.value = getApiErrorMessage(data, '用户名或密码错误，请重试')
      return
    }

    saveAuthSession(data)
    redirectAfterAuth()
  } catch {
    errorMsg.value = '网络异常，请稍后重试'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!username.value.trim() || !password.value.trim()) {
    errorMsg.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value.trim(), password: password.value.trim() }),
    })

    const data = await res.json().catch(() => null)

    if (!res.ok) {
      errorMsg.value = getApiErrorMessage(data, '注册失败，请稍后重试')
      return
    }

    saveAuthSession(data)
    redirectAfterAuth()
  } catch {
    errorMsg.value = '网络异常，请稍后重试'
  } finally {
    loading.value = false
  }
}

function handleSubmit() {
  if (mode.value === 'login') handleLogin()
  else handleRegister()
}
</script>

<template>
  <div
    style="
      min-height: 100vh;
      background-color: #f8f9ff;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px 16px;
    "
  >
    <div
      style="
        width: 100%;
        max-width: 380px;
        border-radius: 20px;
        padding: 36px 32px 32px;
        background: #ffffff;
        box-shadow: 0 20px 60px rgba(30,58,138,0.12);
        border: 1px solid rgba(197,197,211,0.25);
        box-sizing: border-box;
      "
    >
      <!-- Header -->
      <div style="margin-bottom: 24px; text-align: center;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 10px;">
          <svg viewBox="0 0 24 24" fill="currentColor" style="width:26px;height:26px;color:#00236f;">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
          </svg>
          <span style="font-weight: 700; font-size: 18px; color: #00236f; font-family: 'Inter', sans-serif;">InterviewAI</span>
        </div>
        <h2 style="font-weight: 700; font-size: 20px; color: #0b1c30; font-family: 'Inter', sans-serif; margin: 0 0 4px;">
          {{ mode === 'login' ? '欢迎回来' : '创建账号' }}
        </h2>
        <p style="font-size: 13px; color: #444651; font-family: 'Inter', sans-serif; margin: 0;">
          {{ mode === 'login' ? '登录以继续你的面试练习' : '注册后即可开始模拟面试' }}
        </p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" novalidate style="display: flex; flex-direction: column; gap: 0;">
        <div style="margin-bottom: 16px;">
          <label style="display: block; font-size: 13px; font-weight: 600; color: #0b1c30; font-family: 'Inter', sans-serif; margin-bottom: 6px;">
            用户名
          </label>
          <input
            v-model="username"
            type="text"
            autocomplete="username"
            placeholder="请输入用户名"
            :disabled="loading"
            :style="`
              display: block; width: 100%; box-sizing: border-box;
              padding: 10px 14px; border-radius: 10px;
              border: 1px solid ${errorMsg ? '#d81e06' : '#c5c5d3'};
              font-size: 14px; font-family: 'Inter', sans-serif;
              color: #0b1c30; background: #f8f9ff; outline: none;
            `"
          />
        </div>

        <div style="margin-bottom: 20px;">
          <label style="display: block; font-size: 13px; font-weight: 600; color: #0b1c30; font-family: 'Inter', sans-serif; margin-bottom: 6px;">
            密码
          </label>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="请输入密码"
            :disabled="loading"
            :style="`
              display: block; width: 100%; box-sizing: border-box;
              padding: 10px 14px; border-radius: 10px;
              border: 1px solid ${errorMsg ? '#d81e06' : '#c5c5d3'};
              font-size: 14px; font-family: 'Inter', sans-serif;
              color: #0b1c30; background: #f8f9ff; outline: none;
            `"
          />
        </div>

        <div
          v-if="errorMsg"
          style="
            margin-bottom: 16px; padding: 10px 14px; border-radius: 10px;
            background: #fff0f0; border: 1px solid #ffd0d0;
            color: #d81e06; font-size: 13px; font-family: 'Inter', sans-serif;
          "
        >
          {{ errorMsg }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          :style="`
            display: flex; align-items: center; justify-content: center; gap: 8px;
            width: 100%; padding: 12px; border-radius: 10px; border: none;
            background-color: #00236f; color: #fff;
            font-size: 14px; font-weight: 600; font-family: 'Inter', sans-serif;
            cursor: ${loading ? 'not-allowed' : 'pointer'};
            opacity: ${loading ? '0.7' : '1'}; transition: opacity 0.2s;
          `"
        >
          <svg v-if="loading" viewBox="0 0 24 24" fill="none" style="width:16px;height:16px;animation:spin 1s linear infinite;">
            <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.3)" stroke-width="3"/>
            <path d="M12 2a10 10 0 0 1 10 10" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
          </svg>
          {{ loading ? (mode === 'login' ? '登录中...' : '注册中...') : (mode === 'login' ? '登 录' : '注 册') }}
        </button>

        <p style="margin: 16px 0 0; text-align: center; font-size: 13px; color: #444651; font-family: 'Inter', sans-serif;">
          <template v-if="mode === 'login'">
            还没有账号？
            <button type="button" style="background: none; border: none; padding: 0; color: #00236f; font-size: 13px; font-weight: 600; font-family: 'Inter', sans-serif; cursor: pointer;" @click="switchMode('register')">免费注册</button>
          </template>
          <template v-else>
            已有账号？
            <button type="button" style="background: none; border: none; padding: 0; color: #00236f; font-size: 13px; font-weight: 600; font-family: 'Inter', sans-serif; cursor: pointer;" @click="switchMode('login')">立即登录</button>
          </template>
        </p>
      </form>
    </div>
  </div>
</template>

<style scoped>
@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
</style>

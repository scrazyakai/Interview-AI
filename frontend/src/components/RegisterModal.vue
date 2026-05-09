<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE_URL, getApiErrorMessage, saveAuthSession } from '../utils/auth'

const emit = defineEmits<{
  close: []
  success: []
}>()

const router = useRouter()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMsg = ref('')

function close() {
  emit('close')
}

async function handleSubmit() {
  errorMsg.value = ''

  if (!username.value.trim() || !password.value.trim()) {
    errorMsg.value = '请输入用户名和密码'
    return
  }
  if (!/^[A-Za-z0-9_]{3,32}$/.test(username.value.trim())) {
    errorMsg.value = '用户名需为 3-32 位字母、数字或下划线'
    return
  }
  if (password.value.length < 3) {
    errorMsg.value = '密码至少需要 3 位字符'
    return
  }
  if (password.value !== confirmPassword.value) {
    errorMsg.value = '两次输入的密码不一致'
    return
  }

  loading.value = true

  try {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value.trim(),
        password: password.value,
      }),
    })

    const data = await res.json().catch(() => null)

    if (!res.ok) {
      errorMsg.value = getApiErrorMessage(data, '注册失败，请稍后重试')
      return
    }

    saveAuthSession(data)
    emit('success')
    emit('close')
    router.push('/interview/setup')
  } catch {
    errorMsg.value = '网络异常，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <!-- Backdrop -->
  <div
    style="
      position: fixed; inset: 0; z-index: 200;
      display: flex; align-items: center; justify-content: center;
      background: rgba(11,28,48,0.5);
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
    "
    @click.self="close"
  >
    <!-- Modal card -->
    <div
      style="
        position: relative;
        width: 100%;
        max-width: 400px;
        margin: 0 16px;
        border-radius: 20px;
        padding: 36px 32px 32px;
        background: #ffffff;
        box-shadow: 0 20px 60px rgba(30,58,138,0.18);
        border: 1px solid rgba(197,197,211,0.25);
        box-sizing: border-box;
      "
    >
      <!-- Close button -->
      <button
        type="button"
        style="
          position: absolute; top: 14px; right: 14px;
          display: flex; align-items: center; justify-content: center;
          width: 32px; height: 32px;
          border: none; background: transparent; border-radius: 50%;
          cursor: pointer; color: #888;
        "
        @click="close"
      >
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:18px;height:18px;">
          <path d="M18 6 6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>

      <!-- Header -->
      <div style="margin-bottom: 24px; text-align: center;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 10px;">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"
               style="width:24px;height:24px;color:#00236f;transform:matrix(-1,0,0,1,0,0);">
            <path d="M13 8.57a1.43 1.43 0 1 0 0 2.86 1.43 1.43 0 0 0 0-2.86z"/>
            <path d="M13 3C9.25 3 6.2 5.94 6.02 9.64L4.1 12.2a.5.5 0 0 0 .4.8H6v3c0 1.1.9 2 2 2h1v3h7v-4.68A6.999 6.999 0 0 0 13 3zm3 7c0 .13-.01.26-.02.39l.83.66c.08.06.1.16.05.25l-.8 1.39c-.05.09-.16.12-.24.09l-.99-.4c-.21.16-.43.29-.67.39L14 13.83c-.01.1-.1.17-.2.17h-1.6c-.1 0-.18-.07-.2-.17l-.15-1.06c-.25-.1-.47-.23-.68-.39l-.99.4c-.09.03-.2 0-.25-.09l-.8-1.39a.19.19 0 0 1 .05-.25l.84-.66c-.01-.13-.02-.26-.02-.39s.02-.27.04-.39l-.85-.66c-.08-.06-.1-.16-.05-.26l.8-1.38c.05-.09.15-.12.24-.09l1 .4c.2-.15.43-.29.67-.39L12 6.17c.02-.1.1-.17.2-.17h1.6c.1 0 .18.07.2.17l.15 1.06c.24.1.46.23.67.39l1-.4c.09-.03.2 0 .24.09l.8 1.38a.2.2 0 0 1-.05.26l-.85.66c.03.12.04.25.04.39z"/>
          </svg>
          <span style="font-weight: 700; font-size: 18px; color: #00236f; font-family: 'Inter', sans-serif;">InterviewAI</span>
        </div>
        <h2 style="font-weight: 700; font-size: 20px; color: #0b1c30; font-family: 'Inter', sans-serif; margin: 0 0 4px;">免费注册</h2>
        <p style="font-size: 13px; color: #444651; font-family: 'Inter', sans-serif; margin: 0;">创建账号，开始你的 AI 面试练习之旅</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" novalidate style="display: flex; flex-direction: column; gap: 0;">
        <!-- Username -->
        <div style="margin-bottom: 14px;">
          <label style="display: block; font-size: 13px; font-weight: 600; color: #0b1c30; font-family: 'Inter', sans-serif; margin-bottom: 6px;">
            用户名
          </label>
          <input
            v-model="username"
            type="text"
            autocomplete="username"
            placeholder="3-32 位字母、数字或下划线"
            :disabled="loading"
            :style="`
              display: block;
              width: 100%;
              box-sizing: border-box;
              padding: 10px 14px;
              border-radius: 10px;
              border: 1px solid ${errorMsg ? '#d81e06' : '#c5c5d3'};
              font-size: 14px;
              font-family: 'Inter', sans-serif;
              color: #0b1c30;
              background: #f8f9ff;
              outline: none;
            `"
          />
        </div>

        <!-- Password -->
        <div style="margin-bottom: 14px;">
          <label style="display: block; font-size: 13px; font-weight: 600; color: #0b1c30; font-family: 'Inter', sans-serif; margin-bottom: 6px;">
            密码
          </label>
          <input
            v-model="password"
            type="password"
            autocomplete="new-password"
            placeholder="请输入密码（至少 3 位）"
            :disabled="loading"
            :style="`
              display: block;
              width: 100%;
              box-sizing: border-box;
              padding: 10px 14px;
              border-radius: 10px;
              border: 1px solid ${errorMsg ? '#d81e06' : '#c5c5d3'};
              font-size: 14px;
              font-family: 'Inter', sans-serif;
              color: #0b1c30;
              background: #f8f9ff;
              outline: none;
            `"
          />
        </div>

        <!-- Confirm Password -->
        <div style="margin-bottom: 20px;">
          <label style="display: block; font-size: 13px; font-weight: 600; color: #0b1c30; font-family: 'Inter', sans-serif; margin-bottom: 6px;">
            确认密码
          </label>
          <input
            v-model="confirmPassword"
            type="password"
            autocomplete="new-password"
            placeholder="再次输入密码"
            :disabled="loading"
            :style="`
              display: block;
              width: 100%;
              box-sizing: border-box;
              padding: 10px 14px;
              border-radius: 10px;
              border: 1px solid ${errorMsg ? '#d81e06' : '#c5c5d3'};
              font-size: 14px;
              font-family: 'Inter', sans-serif;
              color: #0b1c30;
              background: #f8f9ff;
              outline: none;
            `"
          />
        </div>

        <!-- Error message -->
        <div
          v-if="errorMsg"
          style="
            margin-bottom: 16px;
            padding: 10px 14px;
            border-radius: 10px;
            background: #fff0f0;
            border: 1px solid #ffd0d0;
            color: #d81e06;
            font-size: 13px;
            font-family: 'Inter', sans-serif;
          "
        >
          {{ errorMsg }}
        </div>

        <!-- Submit -->
        <button
          type="submit"
          :disabled="loading"
          :style="`
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            padding: 12px;
            border-radius: 10px;
            border: none;
            background-color: #00236f;
            color: #fff;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            cursor: ${loading ? 'not-allowed' : 'pointer'};
            opacity: ${loading ? '0.7' : '1'};
            transition: opacity 0.2s;
          `"
        >
          <svg v-if="loading" viewBox="0 0 24 24" fill="none" style="width:16px;height:16px;animation:spin 1s linear infinite;">
            <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.3)" stroke-width="3"/>
            <path d="M12 2a10 10 0 0 1 10 10" stroke="#fff" stroke-width="3" stroke-linecap="round"/>
          </svg>
          {{ loading ? '注册中...' : '免费注册' }}
        </button>

        <!-- Switch to login hint -->
        <p style="margin: 16px 0 0; text-align: center; font-size: 13px; color: #444651; font-family: 'Inter', sans-serif;">
          已有账号？
          <button
            type="button"
            style="background: none; border: none; padding: 0; color: #00236f; font-size: 13px; font-weight: 600; font-family: 'Inter', sans-serif; cursor: pointer;"
            @click="$emit('switch-to-login')"
          >立即登录</button>
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

<script setup lang="ts">
import { ref } from 'vue'
import { API_BASE_URL, getApiErrorMessage, saveAuthSession } from '../utils/auth'

const emit = defineEmits<{
  close: []
  success: []
  'switch-to-register': []
}>()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

function close() {
  emit('close')
}

async function handleSubmit() {
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
      body: JSON.stringify({
        username: username.value.trim(),
        password: password.value.trim(),
      }),
    })

    const data = await res.json().catch(() => null)

    if (!res.ok) {
      errorMsg.value = getApiErrorMessage(data, '用户名或密码错误，请重试')
      return
    }

    saveAuthSession(data)
    emit('success')
    emit('close')
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
        max-width: 380px;
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
          <svg viewBox="0 0 24 24" fill="currentColor" style="width:26px;height:26px;color:#00236f;">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
          </svg>
          <span style="font-weight: 700; font-size: 18px; color: #00236f; font-family: 'Inter', sans-serif;">InterviewAI</span>
        </div>
        <h2 style="font-weight: 700; font-size: 20px; color: #0b1c30; font-family: 'Inter', sans-serif; margin: 0 0 4px;">欢迎回来</h2>
        <p style="font-size: 13px; color: #444651; font-family: 'Inter', sans-serif; margin: 0;">登录以继续你的面试练习</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" novalidate style="display: flex; flex-direction: column; gap: 0;">
        <!-- Username -->
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
          {{ loading ? '登录中...' : '登 录' }}
        </button>

        <!-- Switch to register hint -->
        <p style="margin: 16px 0 0; text-align: center; font-size: 13px; color: #444651; font-family: 'Inter', sans-serif;">
          还没有账号？
          <button
            type="button"
            style="background: none; border: none; padding: 0; color: #00236f; font-size: 13px; font-weight: 600; font-family: 'Inter', sans-serif; cursor: pointer;"
            @click="$emit('switch-to-register')"
          >免费注册</button>
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

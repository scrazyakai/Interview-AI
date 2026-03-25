<template>
  <main class="homePage">
    <AppTopbar
      :on-home="true"
      @login="openAuthDialog('login')"
      @register="openAuthDialog('register')"
      @logout="logout"
    />

    <section class="heroSection">
      <div class="heroCopy">
        <p class="eyebrow">AI Mock Interview</p>
        <h1>先创建面试配置，再进入实时模拟面试</h1>
        <p class="heroText">
          现在的模拟面试流程会先让你选择岗位、经验级别、面试模式，并填写岗位描述，随后调用
          `/api/interview/create-session` 创建本次面试，再进入实时语音面试页面。
        </p>
        <div class="heroActions">
          <button class="primaryButton largeButton" type="button" @click="handlePrimaryAction">
            {{ activeUser ? '创建面试并开始' : '登录后开始面试' }}
          </button>
          <button class="ghostButton largeButton" type="button" @click="scrollToFeatures">查看流程</button>
        </div>
      </div>

      <div class="heroPanel">
        <div class="panelCard">
          <p class="panelLabel">新的面试流程</p>
          <ol class="stepList">
            <li>选择岗位：前端、后端、测试、运维、全栈</li>
            <li>选择经验级别和面试模式</li>
            <li>填写岗位描述并创建面试 session</li>
            <li>进入 `interview` 页面打开麦克风开始面试</li>
          </ol>
        </div>
      </div>
    </section>

    <section id="features" class="contentSection">
      <div class="sectionHeader">
        <p class="eyebrow">Why This Flow</p>
        <h2>把面试准备前置，避免直接进入空白面试页</h2>
      </div>

      <div class="featureGrid">
        <article class="featureCard">
          <h3>必填面试信息</h3>
          <p>进入面试前必须完成岗位、经验级别、模式和岗位描述，避免上下文缺失。</p>
        </article>
        <article class="featureCard">
          <h3>先创建 session</h3>
          <p>前端会先请求 `/api/interview/create-session`，后端完成初始化后再进入面试页面。</p>
        </article>
        <article class="featureCard">
          <h3>实时语音继续保留</h3>
          <p>进入 `interview` 页面后，依然可以直接开启麦克风、发送语音和文字消息。</p>
        </article>
      </div>
    </section>

    <div v-if="authDialogOpen" class="authOverlay">
      <section class="authDialog">
        <button class="closeButton" type="button" @click="closeAuthDialog">×</button>
        <p class="eyebrow">{{ authMode === 'login' ? '登录账号' : '注册账号' }}</p>
        <h2>{{ authTitle }}</h2>
        <p class="authDescription">{{ authDescription }}</p>

        <form class="authForm" @submit.prevent="submitAuthForm">
          <label class="fieldBlock">
            <span class="fieldLabel">用户名</span>
            <input
              v-model.trim="authForm.username"
              class="fieldInput"
              type="text"
              minlength="3"
              maxlength="32"
              pattern="[A-Za-z0-9]+"
              placeholder="请输入英文或数字用户名"
            />
          </label>

          <label class="fieldBlock">
            <span class="fieldLabel">密码</span>
            <input
              v-model.trim="authForm.password"
              class="fieldInput"
              type="password"
              minlength="3"
              maxlength="128"
              placeholder="请输入密码"
            />
          </label>

          <p v-if="authError" class="messageBanner messageError">{{ authError }}</p>
          <p v-if="authSuccess" class="messageBanner messageSuccess">{{ authSuccess }}</p>

          <button class="primaryButton authSubmit" type="submit" :disabled="authLoading">
            {{ authLoading ? '提交中...' : authSubmitLabel }}
          </button>
        </form>

        <button class="switchButton" type="button" @click="toggleAuthMode">
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
    ? '登录后即可创建面试 session 并进入模拟面试。'
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

<style scoped>
.homePage {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
  color: #0f172a;
}
.heroSection,
.contentSection {
  width: min(1200px, calc(100% - 32px));
  margin: 0 auto;
}
.heroSection {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 24px;
  padding: 40px 0 56px;
}
.eyebrow {
  margin: 0 0 10px;
  color: #1d4ed8;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.heroCopy h1,
.sectionHeader h2 {
  margin: 0 0 14px;
  font-size: 42px;
  line-height: 1.1;
}
.heroText,
.featureCard p,
.authDescription {
  color: #475569;
  line-height: 1.8;
}
.heroActions {
  display: flex;
  gap: 12px;
  align-items: center;
}
.primaryButton,
.ghostButton,
.closeButton,
.switchButton {
  border-radius: 999px;
  font: inherit;
}
.ghostButton,
.switchButton {
  border: 1px solid #cbd5e1;
  background: #fff;
  color: #0f172a;
}
.ghostButton {
  min-height: 42px;
  padding: 0 16px;
  cursor: pointer;
}
.primaryButton {
  border: 0;
  background: #111827;
  color: #fff;
  min-height: 42px;
  padding: 0 18px;
  cursor: pointer;
}
.largeButton {
  min-height: 48px;
  padding: 0 20px;
}
.heroPanel,
.featureCard,
.authDialog {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
}
.panelCard {
  padding: 28px;
}
.panelLabel {
  margin: 0 0 12px;
  color: #92400e;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.stepList {
  margin: 0;
  padding-left: 20px;
  line-height: 1.9;
}
.contentSection {
  padding-bottom: 56px;
}
.featureGrid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}
.featureCard {
  padding: 24px;
}
.featureCard h3 {
  margin: 0 0 10px;
}
.authOverlay {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  padding: 16px;
  background: rgba(15, 23, 42, 0.45);
}
.authDialog {
  position: relative;
  width: min(480px, 100%);
  padding: 28px;
}
.closeButton {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border: 0;
  background: #e2e8f0;
  cursor: pointer;
}
.authForm {
  display: grid;
  gap: 14px;
}
.fieldBlock {
  display: grid;
  gap: 8px;
}
.fieldLabel {
  font-size: 13px;
  font-weight: 700;
}
.fieldInput {
  min-height: 46px;
  padding: 0 14px;
  border: 1px solid #cbd5e1;
  border-radius: 16px;
  background: #f8fafc;
  font: inherit;
}
.messageBanner {
  margin: 0;
  padding: 12px 14px;
  border-radius: 14px;
  font-size: 14px;
}
.messageError {
  background: #fee2e2;
  color: #991b1b;
}
.messageSuccess {
  background: #dcfce7;
  color: #166534;
}
.authSubmit {
  width: 100%;
}
.switchButton {
  margin-top: 12px;
  width: 100%;
  min-height: 42px;
  cursor: pointer;
}
@media (max-width: 900px) {
  .heroSection,
  .contentSection {
    width: calc(100% - 24px);
  }
  .heroSection,
  .featureGrid {
    grid-template-columns: 1fr;
  }
  .heroActions {
    width: 100%;
    flex-wrap: wrap;
  }
  .primaryButton,
  .ghostButton,
  .largeButton {
    width: 100%;
  }
  .heroCopy h1,
  .sectionHeader h2 {
    font-size: 32px;
  }
}
</style>

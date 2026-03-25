<template>
  <div class="setupPage">
    <AppTopbar @logout="logout" />

    <main class="setupShell">
      <section class="setupHero">
        <p class="setupEyebrow">Interview Setup</p>
        <h1 class="setupTitle">先完成面试配置，再进入模拟面试</h1>
        <p class="setupDescription">
          这里会先调用 `/api/interview/create-session` 创建本次面试记录。创建成功后，我们再进入实时面试页面。
        </p>
      </section>

      <section class="setupCard">
        <div class="cardHeader">
          <h2>面试信息</h2>
          <p>岗位和模式是必填项，岗位描述支持自由输入。</p>
        </div>

        <form class="setupForm" @submit.prevent="submitSetup">
          <label class="fieldBlock">
            <span class="fieldLabel">岗位方向</span>
            <select v-model="form.job_title" class="fieldControl" :disabled="submitting">
              <option v-for="option in jobTitleOptions" :key="option" :value="option">
                {{ option }}
              </option>
            </select>
          </label>

          <label class="fieldBlock">
            <span class="fieldLabel">经验级别</span>
            <select v-model="form.experience_level" class="fieldControl" :disabled="submitting">
              <option v-for="option in experienceLevelOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>

          <label class="fieldBlock">
            <span class="fieldLabel">面试模式</span>
            <select v-model="form.mode" class="fieldControl" :disabled="submitting">
              <option v-for="option in modeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>

          <div class="fieldBlock">
            <span class="fieldLabel">上传简历</span>

            <div class="resumeUploadPanel">
              <label class="uploadButton" :class="{ uploadButtonDisabled: submitting || resumeUploading }">
                <input
                  class="uploadInput"
                  type="file"
                  accept="application/pdf,.pdf"
                  :disabled="submitting || resumeUploading"
                  @change="handleResumeChange"
                />
                {{ resumeUploading ? '上传中...' : resumeUploaded ? '重新上传 PDF' : '选择 PDF 简历' }}
              </label>

              <p class="uploadMeta">{{ resumeFileName || '尚未上传简历' }}</p>
            </div>
          </div>

          <label class="fieldBlock fieldBlockFull">
            <span class="fieldLabel">岗位描述</span>
            <textarea
              v-model.trim="form.job_description"
              class="fieldTextarea"
              rows="6"
              maxlength="2000"
              placeholder="请输入本次面试想考察的岗位描述、技术栈、职责范围或 JD 重点..."
              :disabled="submitting"
            ></textarea>
          </label>

          <p v-if="errorMessage" class="messageBanner messageError">{{ errorMessage }}</p>
          <p v-if="successMessage" class="messageBanner messageSuccess">{{ successMessage }}</p>

          <div class="actionsRow">
            <button class="secondaryButton" type="button" :disabled="submitting" @click="goHome">
              返回首页
            </button>
            <button class="primaryButton" type="submit" :disabled="submitting || resumeUploading || !isFormValid">
              {{ submitting ? '创建中...' : '创建面试并进入' }}
            </button>
          </div>
        </form>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import AppTopbar from '../components/AppTopbar.vue'
import {
  API_BASE_URL,
  clearAuthSession,
  loadAuthSession,
  saveInterviewSetup,
  type InterviewSetupPayload,
} from '../utils/auth'

const router = useRouter()
const jobTitleOptions = ['前端', '后端', '测试', '运维', '全栈']
const experienceLevelOptions = [
  { label: '应届生', value: 'intern' },
  { label: '初级', value: 'junior' },
  { label: '中级', value: 'mid' },
  { label: '高级', value: 'senior' },
]
const modeOptions = [
  { value: 'technical', label: '技术面' },
  { value: 'behavioral', label: '行为面' },
  { value: 'mixed', label: '综合面' },
]

const defaultJobTitle = jobTitleOptions[0] ?? '前端'
const defaultExperienceLevel = experienceLevelOptions[0]?.value ?? 'intern'
const defaultMode = modeOptions[0]?.value ?? 'technical'

const form = reactive<InterviewSetupPayload>({
  job_title: defaultJobTitle,
  job_description: '',
  experience_level: defaultExperienceLevel,
  mode: defaultMode,
  resume_text: '',
})

const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const resumeUploading = ref(false)
const resumeUploaded = ref(false)
const resumeFileName = ref('')

const isFormValid = computed(() => form.job_description.trim().length > 0)

function logout() {
  clearAuthSession()
  router.push('/')
}

function goHome() {
  router.push('/')
}

function resetResumeState() {
  form.resume_text = ''
  resumeUploaded.value = false
}

async function handleResumeChange(event: Event) {
  errorMessage.value = ''
  successMessage.value = ''

  const input = event.target as HTMLInputElement | null
  const file = input?.files?.[0]
  if (!input || !file) return

  const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
  if (!isPdf) {
    resumeFileName.value = ''
    resetResumeState()
    errorMessage.value = '仅支持上传 PDF 简历。'
    input.value = ''
    return
  }

  resumeUploading.value = true
  resumeFileName.value = file.name

  try {
    const payload = new FormData()
    payload.append('file', file)

    const response = await fetch(`${API_BASE_URL}/interview/upload`, {
      method: 'POST',
      body: payload,
    })

    const data = (await response.json().catch(() => null)) as
      | { resume_text?: string; detail?: string; message?: string }
      | null

    if (!response.ok) {
      resumeFileName.value = ''
      resetResumeState()
      errorMessage.value = data?.detail ?? data?.message ?? '简历上传失败，请稍后重试。'
      input.value = ''
      return
    }

    form.resume_text = data?.resume_text ?? ''
    resumeUploaded.value = true
  } catch (error) {
    resumeFileName.value = ''
    resetResumeState()
    errorMessage.value = error instanceof Error ? error.message : '简历上传失败，请稍后重试。'
    input.value = ''
  } finally {
    resumeUploading.value = false
  }
}

async function submitSetup() {
  errorMessage.value = ''
  successMessage.value = ''

  const session = loadAuthSession()
  if (!session?.access_token) {
    errorMessage.value = '请先登录，再创建面试。'
    router.push('/')
    return
  }

  if (!isFormValid.value) {
    errorMessage.value = '请先填写岗位描述。'
    return
  }

  if (resumeUploading.value) {
    errorMessage.value = '简历仍在上传处理中，请稍后再提交。'
    return
  }

  submitting.value = true

  try {
    const response = await fetch(`${API_BASE_URL}/interview/create-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${session.access_token}`,
      },
      body: JSON.stringify({
        job_title: form.job_title,
        job_description: form.job_description.trim(),
        experience_level: form.experience_level,
        mode: form.mode,
        resume_text: form.resume_text,
      }),
    })

    const data = (await response.json().catch(() => null)) as
      | boolean
      | { detail?: string; message?: string }
      | null

    if (!response.ok) {
      const errorData = data as { detail?: string; message?: string } | null
      errorMessage.value = errorData?.detail ?? errorData?.message ?? '创建面试失败，请稍后重试。'
      return
    }

    saveInterviewSetup({
      job_title: form.job_title,
      job_description: form.job_description.trim(),
      experience_level: form.experience_level,
      mode: form.mode,
      resume_text: form.resume_text,
    })

    successMessage.value = '面试已创建，正在进入面试页面。'
    router.push('/interview')
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '请求创建面试接口失败。'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.setupPage {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
}

.setupShell {
  width: min(960px, calc(100% - 32px));
  margin: 0 auto;
  padding: 40px 0 56px;
}

.setupHero {
  margin-bottom: 24px;
}

.setupEyebrow {
  margin: 0 0 8px;
  color: #1d4ed8;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.setupTitle {
  margin: 0 0 12px;
  color: #0f172a;
  font-size: 36px;
  line-height: 1.1;
}

.setupDescription {
  margin: 0;
  color: #475569;
  font-size: 15px;
  line-height: 1.8;
}

.setupCard {
  padding: 28px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
}

.cardHeader h2 {
  margin: 0 0 8px;
  color: #111827;
  font-size: 24px;
}

.cardHeader p {
  margin: 0 0 20px;
  color: #64748b;
}

.setupForm {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  align-items: start;
}

.fieldBlock {
  display: grid;
  gap: 8px;
  min-width: 0;
}

.fieldBlockFull {
  grid-column: 1 / -1;
}

.fieldLabel {
  color: #334155;
  font-size: 13px;
  font-weight: 700;
}

.fieldControl,
.fieldTextarea {
  width: 100%;
  border: 1px solid #cbd5e1;
  border-radius: 16px;
  background: #f8fafc;
  color: #0f172a;
  font: inherit;
}

.fieldControl {
  min-height: 46px;
  padding: 0 14px;
}

.fieldTextarea {
  padding: 14px;
  resize: vertical;
  line-height: 1.7;
}

.resumeUploadPanel {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 46px;
  padding: 0 14px;
  border: 1px dashed #cbd5e1;
  border-radius: 16px;
  background: #f8fafc;
  overflow: hidden;
}

.uploadButton {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: none;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: #111827;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
}

.uploadButtonDisabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.uploadInput {
  display: none;
}

.uploadMeta {
  flex: 1 1 auto;
  min-width: 0;
  margin: 0;
  color: #334155;
  font-size: 13px;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.messageBanner {
  grid-column: 1 / -1;
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

.actionsRow {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.primaryButton,
.secondaryButton {
  min-width: 144px;
  min-height: 44px;
  padding: 0 18px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.primaryButton {
  border: 0;
  background: #111827;
  color: #fff;
}

.secondaryButton {
  border: 1px solid #cbd5e1;
  background: #fff;
  color: #0f172a;
}

.primaryButton:disabled,
.secondaryButton:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 720px) {
  .setupShell {
    width: calc(100% - 24px);
    padding: 24px 0 40px;
  }

  .setupCard {
    padding: 20px;
  }

  .setupTitle {
    font-size: 30px;
  }

  .setupForm {
    grid-template-columns: 1fr;
  }

  .actionsRow {
    flex-direction: column-reverse;
  }

  .primaryButton,
  .secondaryButton {
    width: 100%;
  }

  .resumeUploadPanel {
    padding: 8px 12px;
  }
}
</style>

<template>
  <main class="px-6 pb-20 pt-24 lg:px-12 lg:pb-24 max-w-[1280px] mx-auto">
    <div class="grid grid-cols-1 gap-12 lg:grid-cols-12 lg:items-start">
      <!-- Left Column: Intro & Feature Cards -->
      <div class="lg:col-span-5 flex flex-col justify-center">
        <p class="font-mono text-xs font-semibold uppercase tracking-[0.2em] text-secondary">
          Interview Setup
        </p>
        <h1 class="mt-4 text-4xl font-bold leading-tight tracking-tight text-primary lg:text-5xl">
          设置您的<br />AI 模拟面试
        </h1>
        <p class="mt-4 text-lg leading-relaxed text-on-surface-variant">
          配置您的会话，以获得针对您的目标角色和经验水平定制的高保真 AI 反馈。
        </p>

        <!-- Hero image card -->
        <div class="relative mt-8 w-full overflow-hidden rounded-xl shadow-xl aspect-video glass-panel">
          <img
            src="../assets/AI-Power-Insight.png"
            alt="AI 面试助手"
            class="h-full w-full object-cover"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-primary/50 to-transparent"></div>
          <div
            class="absolute bottom-4 left-4 flex items-center gap-1.5 rounded-full border border-white/20 bg-surface/90 px-3 py-1.5 shadow-sm backdrop-blur-sm"
          >
            <span class="material-symbols-outlined text-secondary" style="font-size:16px;">psychology</span>
            <span class="font-mono text-[11px] font-semibold uppercase tracking-widest text-primary">AI-Powered Insights</span>
          </div>
        </div>

        <!-- Feature cards -->
        <div class="mt-6 glass-panel rounded-xl p-6 space-y-4">
          <div class="flex items-start gap-3">
            <div class="shrink-0 rounded-lg bg-secondary-container p-1.5 text-on-secondary-container">
              <span class="material-symbols-outlined" style="font-size:20px;">check_circle</span>
            </div>
            <div>
              <p class="text-sm font-semibold text-on-surface">个性化定制</p>
              <p class="mt-0.5 text-sm text-on-surface-variant">上传简历有助于我们模拟真实的面试环节，AI 会围绕你的经历深度追问。</p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <div class="shrink-0 rounded-lg bg-secondary-container p-1.5 text-on-secondary-container">
              <span class="material-symbols-outlined" style="font-size:20px;">description</span>
            </div>
            <div>
              <p class="text-sm font-semibold text-on-surface">岗位精准匹配</p>
              <p class="mt-0.5 text-sm text-on-surface-variant">填写岗位描述后，AI 将聚焦该职位的核心考察点，生成高质量题目。</p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <div class="shrink-0 rounded-lg bg-secondary-container p-1.5 text-on-secondary-container">
              <span class="material-symbols-outlined" style="font-size:20px;">analytics</span>
            </div>
            <div>
              <p class="text-sm font-semibold text-on-surface">面试结束即出报告</p>
              <p class="mt-0.5 text-sm text-on-surface-variant">每次练习结束后自动生成评分报告与个性化改进建议。</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Setup Form -->
      <div class="lg:col-span-7">
        <div class="glass-modal rounded-xl border border-outline-variant/10 shadow-[0_10px_30px_rgba(30,58,138,0.05)]">
          <FormSection
            :job-title="form.job_title"
            :experience-level="form.experience_level"
            :mode="form.mode"
            :job-description="form.job_description"
            :resume-file-name="resumeFileName"
            :helper-tip="setupPageMock.helperTip"
            :loading="submitting"
            :disable-submit="isSubmitDisabled"
            :error-message="errorMessage"
            :job-title-options="jobTitleOptions"
            :experience-level-options="experienceLevelOptions"
            :mode-options="modeOptions"
            @update:job-title="form.job_title = $event"
            @update:experience-level="form.experience_level = $event"
            @update:mode="form.mode = $event"
            @update:job-description="form.job_description = $event"
            @file-selected="handleResumeFile"
            @back="goHome"
            @submit="submitSetup"
          />
        </div>

        <!-- Ready Check -->
        <div class="mt-4 rounded-xl border border-outline-variant/20 bg-surface-container-low p-4">
          <p class="font-mono text-[11px] font-semibold uppercase tracking-[0.22em] text-on-surface-variant">Ready Check</p>
          <div class="mt-3 space-y-3">
            <div class="flex items-start gap-3 rounded-lg bg-surface-container-lowest px-4 py-3">
              <span
                class="mt-1.5 inline-flex h-2 w-2 shrink-0 rounded-full"
                :class="resumeFileName ? 'bg-secondary' : 'bg-outline-variant'"
              ></span>
              <div>
                <p class="text-sm font-semibold text-on-surface">简历资料</p>
                <p class="mt-0.5 text-sm text-on-surface-variant">
                  {{ resumeFileName ? `已上传 ${resumeFileName}` : '可选，但上传后 AI 能更准确追问项目经历。' }}
                </p>
              </div>
            </div>
            <div class="flex items-start gap-3 rounded-lg bg-surface-container-lowest px-4 py-3">
              <span
                class="mt-1.5 inline-flex h-2 w-2 shrink-0 rounded-full"
                :class="form.job_description.trim() ? 'bg-secondary' : 'bg-outline-variant'"
              ></span>
              <div>
                <p class="text-sm font-semibold text-on-surface">岗位描述</p>
                <p class="mt-0.5 text-sm text-on-surface-variant">
                  {{ form.job_description.trim() ? '已填写岗位说明，面试问题会更聚焦。' : '这是启动面试的必填项，建议写清技术栈与考察重点。' }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Pro Tip -->
        <div class="mt-4 flex items-start gap-4 glass-panel rounded-xl p-4 border border-secondary-container/30">
          <div class="shrink-0 flex h-10 w-10 items-center justify-center rounded-lg bg-secondary-container text-on-secondary-container">
            <span class="material-symbols-outlined" style="font-variation-settings:'FILL' 1; font-size:20px;">stars</span>
          </div>
          <div>
            <p class="text-sm font-bold text-primary">Pro Tip</p>
            <p class="mt-0.5 text-sm leading-relaxed text-on-surface-variant">{{ setupPageMock.avgStartTip }}。高级职位面试默认包含系统设计与架构权衡题目。</p>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- Mobile Bottom Nav -->
  <nav
    class="md:hidden fixed bottom-0 left-0 w-full z-50 bg-surface/80 backdrop-blur-lg border-t border-outline-variant/20 shadow-[0_-10px_30px_rgba(30,58,138,0.05)] rounded-t-xl flex justify-around items-center px-4 py-2"
  >
    <button
      type="button"
      class="flex flex-col items-center justify-center text-on-surface-variant px-4 py-1 rounded-full transition hover:bg-surface-container-high"
      @click="goHome"
    >
      <span class="material-symbols-outlined" style="font-size:22px;">home</span>
      <span class="font-mono text-[10px] font-semibold uppercase tracking-wider mt-0.5">首页</span>
    </button>
    <div class="flex flex-col items-center justify-center bg-primary-container text-on-primary-container rounded-full px-4 py-1">
      <span class="material-symbols-outlined" style="font-size:22px;">video_chat</span>
      <span class="font-mono text-[10px] font-semibold uppercase tracking-wider mt-0.5">面试</span>
    </div>
    <button
      type="button"
      class="flex flex-col items-center justify-center text-on-surface-variant px-4 py-1 rounded-full transition hover:bg-surface-container-high"
    >
      <span class="material-symbols-outlined" style="font-size:22px;">analytics</span>
      <span class="font-mono text-[10px] font-semibold uppercase tracking-wider mt-0.5">结果</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import FormSection from '../components/setup/FormSection.vue'
import { experienceLevelOptions, jobTitleOptions, modeOptions } from '../constants/interviewOptions'
import { setupPageMock } from '../mock/interviewSetupMock'
import { createInterviewSession, saveInterviewSetup, type InterviewSetupPayload } from '../utils/auth'

const route = useRoute()
const router = useRouter()

const defaultJobTitle = jobTitleOptions[0] ?? '前端'
const defaultExperienceLevel = experienceLevelOptions[0]?.value ?? 'intern'
const defaultMode = modeOptions[0]?.value ?? 'technical'

const form = reactive<InterviewSetupPayload>({
  job_title: defaultJobTitle,
  job_description: '',
  experience_level: defaultExperienceLevel,
  mode: defaultMode,
  resume_text: '',
  session_uuid: '',
})

const submitting = ref(false)
const errorMessage = ref('')
const resumeFileName = ref('')

applyPrefillFromQuery()

const isSubmitDisabled = computed(() => form.job_description.trim().length === 0)

function getSingleQueryValue(value: unknown): string | null {
  if (typeof value === 'string') return value
  if (Array.isArray(value) && typeof value[0] === 'string') return value[0]
  return null
}

function applyPrefillFromQuery() {
  const prefillJobTitle = getSingleQueryValue(route.query.job_title)
  const prefillExperienceLevel = getSingleQueryValue(route.query.experience_level)

  if (prefillJobTitle && jobTitleOptions.includes(prefillJobTitle as (typeof jobTitleOptions)[number])) {
    form.job_title = prefillJobTitle
  }

  if (
    prefillExperienceLevel &&
    experienceLevelOptions.some((option) => option.value === prefillExperienceLevel)
  ) {
    form.experience_level = prefillExperienceLevel
  }
}

function goHome() {
  router.push('/')
}

function handleResumeFile(file: File) {
  errorMessage.value = ''
  const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')

  if (!isPdf) {
    resumeFileName.value = ''
    form.resume_text = ''
    errorMessage.value = '仅支持上传 PDF 简历。'
    return
  }

  resumeFileName.value = file.name
  form.resume_text = `mock_resume: ${file.name}`
}

async function submitSetup() {
  errorMessage.value = ''

  if (isSubmitDisabled.value) {
    errorMessage.value = '请先填写岗位描述。'
    return
  }

  submitting.value = true

  try {
    const session = await createInterviewSession({
      job_title: form.job_title,
      job_description: form.job_description.trim(),
      experience_level: form.experience_level,
      mode: form.mode,
      resume_text: form.resume_text,
    })

    form.session_uuid = session.session_uuid

    saveInterviewSetup({
      job_title: form.job_title,
      job_description: form.job_description.trim(),
      experience_level: form.experience_level,
      mode: form.mode,
      resume_text: form.resume_text,
      session_uuid: form.session_uuid,
    })

    router.push('/interview')
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '创建面试会话失败，请稍后重试。'
  } finally {
    submitting.value = false
  }
}
</script>

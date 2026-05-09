<template>
  <main class="px-6 pt-16 lg:px-12 max-w-[1280px] mx-auto h-screen overflow-hidden flex flex-col">
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-12 flex-1 overflow-hidden py-3">
      <!-- Left Column: Intro & Feature Cards -->
      <div class="lg:col-span-5 flex flex-col overflow-y-auto h-full pr-1">
        <p class="font-mono text-xs font-semibold uppercase tracking-[0.2em] text-secondary">
          Interview Setup
        </p>
        <h1 class="mt-2 text-3xl font-bold leading-tight tracking-tight text-primary lg:text-4xl">
          设置您的面试
        </h1>
        <p class="mt-2 text-base leading-relaxed text-on-surface-variant">
          配置您的会话，以获得针对您的目标角色和经验水平定制的高保真 AI 反馈。
        </p>

        <!-- Hero image card -->
        <div class="relative mt-4 w-full overflow-hidden rounded-xl shadow-xl aspect-video glass-panel">
          <img
            src="../assets/AI-Power-Insight.png"
            alt="AI 面试助手"
            class="h-full w-full object-cover"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-primary/50 to-transparent"></div>
          <div
            class="absolute bottom-4 left-4 flex items-center gap-1.5 rounded-full border border-white/20 bg-surface/90 px-3 py-1.5 shadow-sm backdrop-blur-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#81f769" width="16" height="16" style="transform: scaleX(-1)"><path d="m15.82 7.22-1 .4c-.21-.16-.43-.29-.67-.39L14 6.17c-.02-.1-.1-.17-.2-.17h-1.6c-.1 0-.18.07-.19.17l-.15 1.06c-.24.1-.47.23-.67.39l-1-.4c-.09-.03-.2 0-.24.09l-.8 1.38a.2.2 0 0 0 .05.26l.85.66c-.03.12-.05.26-.05.39s.01.26.03.39l-.84.66a.19.19 0 0 0-.05.25l.8 1.39c.05.09.15.12.25.09l.99-.4c.21.16.43.29.68.39l.14 1.06c.02.1.1.17.2.17h1.6c.1 0 .18-.07.2-.17l.15-1.06c.24-.1.47-.23.67-.39l.99.4c.09.04.2 0 .24-.09l.8-1.39c.05-.09.03-.19-.05-.25l-.83-.66a2.561 2.561 0 0 0 0-.78l.85-.66a.2.2 0 0 0 .05-.26l-.8-1.38c-.05-.09-.16-.12-.25-.09zM13 11.43a1.43 1.43 0 1 1 0-2.86 1.43 1.43 0 0 1 0 2.86z"/><path d="M19.94 9.06c-.43-3.27-3.23-5.86-6.53-6.05C13.27 3 13.14 3 13 3 9.47 3 6.57 5.61 6.08 9l-1.93 3.48c-.41.66.07 1.52.85 1.52h1v2c0 1.1.9 2 2 2h1v3h7v-4.68a7.016 7.016 0 0 0 3.94-7.26zm-5.05 5.57-.89.42V19h-3v-3H8v-4H6.7l1.33-2.33C8.21 7.06 10.35 5 13 5c2.76 0 5 2.24 5 5 0 2.09-1.29 3.88-3.11 4.63z"/></svg>
            <span class="font-mono text-[11px] font-semibold uppercase tracking-widest text-primary">AI-Powered Insights</span>
          </div>
        </div>

        <!-- Feature cards -->
        <div class="mt-3 glass-panel rounded-xl p-4 space-y-3">
          <div class="flex items-start gap-3">
            <div class="shrink-0 rounded-lg bg-secondary-container p-1.5 text-on-secondary-container">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.88-11.71L10 14.17l-1.88-1.88a.996.996 0 1 0-1.41 1.41l2.59 2.59c.39.39 1.02.39 1.41 0L17.3 9.7a.996.996 0 0 0 0-1.41c-.39-.39-1.03-.39-1.42 0z"></path></svg>
            </div>
            <div>
              <p class="text-sm font-semibold text-on-surface">个性化定制</p>
              <p class="mt-0.5 text-sm text-on-surface-variant">上传简历有助于我们模拟真实的面试环节，AI 会围绕你的经历深度追问。</p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <div class="shrink-0 rounded-lg bg-secondary-container p-1.5 text-on-secondary-container">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;"><path d="M8 16h8v2H8zm0-4h8v2H8zm6-10H6c-1.1 0-2 .9-2 2v16c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z"></path></svg>
            </div>
            <div>
              <p class="text-sm font-semibold text-on-surface">岗位精准匹配</p>
              <p class="mt-0.5 text-sm text-on-surface-variant">填写岗位描述后，AI 将聚焦该职位的核心考察点，生成高质量题目。</p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <div class="shrink-0 rounded-lg bg-secondary-container p-1.5 text-on-secondary-container">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"></path><path d="M7 12h2v5H7zm8-5h2v10h-2zm-4 7h2v3h-2zm0-4h2v2h-2z"></path></svg>
            </div>
            <div>
              <p class="text-sm font-semibold text-on-surface">面试结束即出报告</p>
              <p class="mt-0.5 text-sm text-on-surface-variant">每次练习结束后自动生成评分报告与个性化改进建议。</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Setup Form -->
      <div class="lg:col-span-7 overflow-y-auto h-full">
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

      </div>
    </div>
  </main>

  <!-- Tips toast (fixed bottom-right) -->
  <Transition name="tip">
    <div
      v-if="showTip"
      class="fixed bottom-6 right-6 z-40 flex w-72 items-start gap-3 rounded-xl border border-secondary-container/40 bg-surface/95 p-4 shadow-[0_10px_30px_rgba(30,58,138,0.12)] backdrop-blur-xl"
    >
      <div class="shrink-0 flex h-8 w-8 items-center justify-center rounded-lg bg-secondary-container text-on-secondary-container">
        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 16 16" style="width:16px;height:16px;"><path d="M2 6a6 6 0 1 1 10.174 4.31c-.203.196-.359.4-.453.619l-.762 1.769A.5.5 0 0 1 10.5 13a.5.5 0 0 1 0 1 .5.5 0 0 1 0 1l-.224.447a1 1 0 0 1-.894.553H6.618a1 1 0 0 1-.894-.553L5.5 15a.5.5 0 0 1 0-1 .5.5 0 0 1 0-1 .5.5 0 0 1-.46-.302l-.761-1.77a2 2 0 0 0-.453-.618A5.98 5.98 0 0 1 2 6m6-5a5 5 0 0 0-3.479 8.592c.263.254.514.564.676.941L5.83 12h4.342l.632-1.467c.162-.377.413-.687.676-.941A5 5 0 0 0 8 1"></path></svg>
      </div>
      <div class="flex-1 min-w-0">
        <p class="font-mono text-[10px] font-semibold uppercase tracking-[0.15em] text-secondary">Tips</p>
        <p class="mt-1 text-xs leading-relaxed text-on-surface-variant">{{ setupPageMock.avgStartTip }}。高级职位面试默认包含系统设计与架构权衡题目。</p>
      </div>
      <button
        type="button"
        class="shrink-0 -mt-0.5 -mr-0.5 flex h-6 w-6 items-center justify-center rounded-full text-outline transition-colors hover:bg-surface-container-high hover:text-on-surface"
        @click="showTip = false"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:14px;height:14px;"><path d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"></path></svg>
      </button>
    </div>
  </Transition>

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
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:22px;height:22px;"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"></path><path d="M7 12h2v5H7zm8-5h2v10h-2zm-4 7h2v3h-2zm0-4h2v2h-2z"></path></svg>
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
const showTip = ref(true)

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

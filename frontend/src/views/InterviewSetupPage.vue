<template>
  <main class="min-h-screen bg-gradient-to-b from-gray-50 to-white px-4 py-10 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-5xl">
      <header class="space-y-4">
        <p class="text-xs font-semibold uppercase tracking-[0.18em] text-gray-500">{{ setupPageMock.eyebrow }}</p>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">{{ setupPageMock.title }}</h1>
        <p class="max-w-2xl text-sm text-gray-600 sm:text-base">{{ setupPageMock.subtitle }}</p>
        <StepIndicator :current="1" />
      </header>

      <section class="mt-8 rounded-2xl border border-gray-100 bg-white p-5 shadow-md sm:p-7">
        <div class="grid gap-6 lg:grid-cols-[1.65fr_1fr] lg:items-start">
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

          <AiPreviewCard :highlights="setupPageMock.aiHighlights" :average-tip="setupPageMock.avgStartTip" />
        </div>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AiPreviewCard from '../components/setup/AiPreviewCard.vue'
import FormSection from '../components/setup/FormSection.vue'
import StepIndicator from '../components/setup/StepIndicator.vue'
import { experienceLevelOptions, jobTitleOptions, modeOptions } from '../constants/interviewOptions'
import { setupPageMock } from '../mock/interviewSetupMock'
import { saveInterviewSetup, type InterviewSetupPayload } from '../utils/auth'

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

  await new Promise((resolve) => {
    window.setTimeout(resolve, 900)
  })

  form.session_uuid = `mock-session-${Date.now()}`

  saveInterviewSetup({
    job_title: form.job_title,
    job_description: form.job_description.trim(),
    experience_level: form.experience_level,
    mode: form.mode,
    resume_text: form.resume_text,
    session_uuid: form.session_uuid,
  })

  submitting.value = false
  router.push('/interview')
}
</script>

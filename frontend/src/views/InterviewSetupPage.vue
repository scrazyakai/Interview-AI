<template>
  <main class="relative overflow-hidden bg-[#f6efe6] px-4 py-8 text-stone-900 sm:px-6 lg:px-8 lg:py-10">
    <div class="pointer-events-none absolute inset-x-0 top-0 h-[380px] bg-[radial-gradient(circle_at_top_left,_rgba(235,158,95,0.28),_transparent_34%),radial-gradient(circle_at_top_right,_rgba(120,85,58,0.16),_transparent_30%)]"></div>
    <div class="pointer-events-none absolute inset-x-0 top-[180px] mx-auto h-[520px] max-w-6xl rounded-[48px] bg-white/24 blur-3xl"></div>

    <div class="relative mx-auto max-w-6xl">

      <section class="mt-6 grid gap-6 lg:grid-cols-[1.45fr_0.9fr] lg:items-start">
        <div class="rounded-[36px] border border-white/60 bg-white/78 p-3 shadow-[0_24px_80px_rgba(79,56,36,0.12)] backdrop-blur sm:p-4">
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

        <div class="space-y-6">
          <AiPreviewCard :highlights="setupPageMock.aiHighlights" :average-tip="setupPageMock.avgStartTip" />

          <aside class="rounded-[32px] border border-white/60 bg-white/72 p-6 shadow-[0_24px_80px_rgba(79,56,36,0.12)] backdrop-blur">
            <p class="text-[11px] font-semibold uppercase tracking-[0.28em] text-stone-500">Ready Check</p>
            <div class="mt-5 space-y-4">
              <div class="flex items-start gap-3 rounded-[22px] bg-[#fff8f1] px-4 py-4">
                <span class="mt-1 inline-flex h-2.5 w-2.5 rounded-full" :class="resumeFileName ? 'bg-emerald-500' : 'bg-amber-500'"></span>
                <div>
                  <p class="font-semibold text-stone-950">简历资料</p>
                  <p class="mt-1 text-sm leading-7 text-stone-600">{{ resumeFileName ? `已上传 ${resumeFileName}` : '可选，但上传后 AI 能更准确追问项目经历。' }}</p>
                </div>
              </div>
              <div class="flex items-start gap-3 rounded-[22px] bg-[#fff8f1] px-4 py-4">
                <span class="mt-1 inline-flex h-2.5 w-2.5 rounded-full" :class="form.job_description.trim() ? 'bg-emerald-500' : 'bg-amber-500'"></span>
                <div>
                  <p class="font-semibold text-stone-950">岗位描述</p>
                  <p class="mt-1 text-sm leading-7 text-stone-600">{{ form.job_description.trim() ? '已填写岗位说明，面试问题会更聚焦。' : '这是启动面试的必填项，建议写清技术栈与考察重点。' }}</p>
                </div>
              </div>
            </div>
          </aside>
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
const experienceLevelLabel = computed(
  () => experienceLevelOptions.find((option) => option.value === form.experience_level)?.label ?? '待选择',
)
const modeLabel = computed(() => modeOptions.find((option) => option.value === form.mode)?.label ?? '待选择')
const resumeStatus = computed(() => (resumeFileName.value ? '简历已准备' : '等待上传简历'))
const jobDescriptionStatus = computed(() =>
  form.job_description.trim()
    ? '岗位描述已补充，AI 可以围绕你的目标职位生成更聚焦的问题。'
    : '还没有填写岗位描述，建议写明技术栈、职责范围和考察重点。',
)

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


<template>
  <div class="rounded-[32px] border border-stone-200/80 bg-[#fffdfa] p-6 shadow-[0_20px_60px_rgba(89,64,43,0.08)]">
    <form class="space-y-8" @submit.prevent="emit('submit')">
      <section class="rounded-[28px] border border-stone-200/80 bg-white p-5">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.26em] text-stone-500">Core Setup</p>
            <h3 class="mt-3 text-xl font-semibold tracking-[-0.03em] text-stone-950">配置本场面试</h3>
          </div>
          <span class="rounded-full bg-[#fff4e8] px-3 py-1 text-xs font-semibold text-[#9f4f22]">Step 1</span>
        </div>

        <div class="mt-5 grid gap-4 sm:grid-cols-2">
          <label class="space-y-2">
            <span class="text-sm font-medium text-stone-600">岗位方向</span>
            <select
              :value="jobTitle"
              class="h-12 w-full rounded-2xl border border-stone-200 bg-[#fffaf5] px-4 text-sm text-stone-800 transition hover:border-[#d89b62] focus:border-[#d89b62] focus:outline-none focus:ring-4 focus:ring-[#f4d0ad]/50"
              :disabled="loading"
              @change="emit('update:jobTitle', ($event.target as HTMLSelectElement).value)"
            >
              <option v-for="option in jobTitleOptions" :key="option" :value="option">{{ option }}</option>
            </select>
          </label>

          <label class="space-y-2">
            <span class="text-sm font-medium text-stone-600">经验级别</span>
            <select
              :value="experienceLevel"
              class="h-12 w-full rounded-2xl border border-stone-200 bg-[#fffaf5] px-4 text-sm text-stone-800 transition hover:border-[#d89b62] focus:border-[#d89b62] focus:outline-none focus:ring-4 focus:ring-[#f4d0ad]/50"
              :disabled="loading"
              @change="emit('update:experienceLevel', ($event.target as HTMLSelectElement).value)"
            >
              <option v-for="option in experienceLevelOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>
        </div>
      </section>

      <section class="rounded-[28px] border border-stone-200/80 bg-white p-5">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.26em] text-stone-500">Interview Mode</p>
            <h3 class="mt-3 text-xl font-semibold tracking-[-0.03em] text-stone-950">选择练习方式</h3>
          </div>
          <span class="rounded-full bg-[#fff4e8] px-3 py-1 text-xs font-semibold text-[#9f4f22]">Step 2</span>
        </div>

        <div class="mt-5 space-y-5">
          <label class="space-y-2">
            <span class="text-sm font-medium text-stone-600">面试模式</span>
            <select
              :value="mode"
              class="h-12 w-full rounded-2xl border border-stone-200 bg-[#fffaf5] px-4 text-sm text-stone-800 transition hover:border-[#d89b62] focus:border-[#d89b62] focus:outline-none focus:ring-4 focus:ring-[#f4d0ad]/50"
              :disabled="loading"
              @change="emit('update:mode', ($event.target as HTMLSelectElement).value)"
            >
              <option v-for="option in modeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </label>

          <div>
            <div class="mb-2 flex items-center justify-between gap-3">
              <span class="text-sm font-medium text-stone-600">上传简历</span>
              <span class="text-xs text-stone-500">支持 PDF</span>
            </div>
            <div
              class="rounded-[24px] border-2 border-dashed p-6 text-center transition"
              :class="isDragOver ? 'border-[#d89b62] bg-[#fff4e8]' : 'border-stone-200 bg-[#fffaf6] hover:border-[#d89b62] hover:bg-[#fff4e8]/70'"
              @dragover.prevent="isDragOver = true"
              @dragleave.prevent="isDragOver = false"
              @drop.prevent="handleDrop"
            >
              <input ref="fileInputRef" class="hidden" type="file" accept="application/pdf,.pdf" :disabled="loading" @change="handleSelect" />
              <button
                type="button"
                class="inline-flex rounded-full border border-stone-200 bg-white px-4 py-2 text-sm font-medium text-stone-700 shadow-sm transition hover:border-[#d89b62] hover:text-stone-950"
                :disabled="loading"
                @click="fileInputRef?.click()"
              >
                上传 PDF 简历
              </button>
              <p class="mt-4 text-sm text-stone-600">拖拽文件到这里，或点击按钮选择本地 PDF。</p>
              <p class="mt-2 text-xs text-stone-500">{{ resumeFileName || '尚未选择文件' }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-[28px] border border-stone-200/80 bg-white p-5">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.26em] text-stone-500">Context Brief</p>
            <h3 class="mt-3 text-xl font-semibold tracking-[-0.03em] text-stone-950">补充岗位背景，让问题更贴近真实需求</h3>
          </div>
          <span class="rounded-full bg-[#fff4e8] px-3 py-1 text-xs font-semibold text-[#9f4f22]">Required</span>
        </div>

        <p class="mt-4 rounded-[20px] bg-[#fff7ef] px-4 py-3 text-sm leading-7 text-[#9f4f22]">{{ helperTip }}</p>
        <textarea
          :value="jobDescription"
          rows="7"
          maxlength="2000"
          :disabled="loading"
          class="mt-4 w-full rounded-[24px] border border-stone-200 bg-[#fffaf5] px-4 py-4 text-sm leading-7 text-stone-800 transition placeholder:text-stone-400 hover:border-[#d89b62] focus:border-[#d89b62] focus:outline-none focus:ring-4 focus:ring-[#f4d0ad]/50"
          placeholder="示例：
- 技术栈：Java / Spring Boot / MySQL
- 岗位：后端开发
- 重点考察：项目经验 + 八股文"
          @input="emit('update:jobDescription', ($event.target as HTMLTextAreaElement).value)"
        ></textarea>
      </section>

      <p v-if="errorMessage" class="rounded-[20px] border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ errorMessage }}</p>

      <div class="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:items-center sm:justify-between">
        <button
          type="button"
          class="h-12 rounded-full border border-stone-300 bg-white px-5 text-sm font-medium text-stone-700 transition hover:border-stone-400 hover:bg-stone-50"
          :disabled="loading"
          @click="emit('back')"
        >
          返回首页
        </button>

        <button
          type="submit"
          class="inline-flex h-12 items-center justify-center rounded-full bg-[linear-gradient(135deg,#1f1710,#9f4f22_58%,#d98952)] px-6 text-sm font-semibold text-white shadow-[0_18px_36px_rgba(159,79,34,0.28)] transition hover:translate-y-[-1px] hover:shadow-[0_22px_42px_rgba(159,79,34,0.34)] disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="disableSubmit || loading"
        >
          {{ loading ? '生成中...' : '创建面试并开始' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  jobTitle: string
  experienceLevel: string
  mode: string
  jobDescription: string
  resumeFileName: string
  helperTip: string
  loading: boolean
  disableSubmit: boolean
  errorMessage: string
  jobTitleOptions: readonly string[]
  experienceLevelOptions: ReadonlyArray<{ label: string; value: string }>
  modeOptions: ReadonlyArray<{ label: string; value: string }>
}>()

const emit = defineEmits<{
  'update:jobTitle': [value: string]
  'update:experienceLevel': [value: string]
  'update:mode': [value: string]
  'update:jobDescription': [value: string]
  'file-selected': [file: File]
  back: []
  submit: []
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragOver = ref(false)

function pickFileFromEvent(event: Event): File | null {
  const input = event.target as HTMLInputElement | null
  return input?.files?.[0] ?? null
}

function handleSelect(event: Event) {
  const file = pickFileFromEvent(event)
  if (!file) return
  emit('file-selected', file)
}

function handleDrop(event: DragEvent) {
  isDragOver.value = false
  const file = event.dataTransfer?.files?.[0]
  if (!file) return
  emit('file-selected', file)
}
</script>

<template>
  <div class="p-6 lg:p-8">
    <form class="space-y-6" @submit.prevent="emit('submit')">

      <!-- Job Title -->
      <div class="space-y-1.5">
        <label class="block font-mono text-xs font-semibold uppercase tracking-[0.05em] text-on-surface-variant">岗位名称</label>
        <div class="relative">
          <select
            :value="jobTitle"
            class="h-12 w-full appearance-none rounded-lg border border-outline-variant bg-white/50 px-6 pr-10 text-sm text-on-surface outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 disabled:opacity-50"
            :disabled="loading"
            @change="emit('update:jobTitle', ($event.target as HTMLSelectElement).value)"
          >
            <option v-for="option in jobTitleOptions" :key="option" :value="option">{{ option }}</option>
          </select>
          <span class="material-symbols-outlined pointer-events-none absolute right-4 top-3 text-outline" style="font-size:20px;">expand_more</span>
        </div>
      </div>

      <!-- Experience Level & Mode -->
      <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div class="space-y-1.5">
          <label class="block font-mono text-xs font-semibold uppercase tracking-[0.05em] text-on-surface-variant">经验等级</label>
          <div class="relative">
            <select
              :value="experienceLevel"
              class="h-12 w-full appearance-none rounded-lg border border-outline-variant bg-white/50 px-6 pr-10 text-sm text-on-surface outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 disabled:opacity-50"
              :disabled="loading"
              @change="emit('update:experienceLevel', ($event.target as HTMLSelectElement).value)"
            >
              <option v-for="option in experienceLevelOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
            <span class="material-symbols-outlined pointer-events-none absolute right-4 top-3 text-outline" style="font-size:20px;">expand_more</span>
          </div>
        </div>
        <div class="space-y-1.5">
          <label class="block font-mono text-xs font-semibold uppercase tracking-[0.05em] text-on-surface-variant">面试模式</label>
          <div class="relative">
            <select
              :value="mode"
              class="h-12 w-full appearance-none rounded-lg border border-outline-variant bg-white/50 px-6 pr-10 text-sm text-on-surface outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 disabled:opacity-50"
              :disabled="loading"
              @change="emit('update:mode', ($event.target as HTMLSelectElement).value)"
            >
              <option v-for="option in modeOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
            <span class="material-symbols-outlined pointer-events-none absolute right-4 top-3 text-outline" style="font-size:20px;">expand_more</span>
          </div>
        </div>
      </div>

      <!-- Job Description -->
      <div class="space-y-1.5">
        <div class="flex items-center justify-between">
          <label class="font-mono text-xs font-semibold uppercase tracking-[0.05em] text-on-surface-variant">岗位描述 (必填)</label>
          <span class="text-sm text-error">* 必填</span>
        </div>
        <textarea
          :value="jobDescription"
          rows="5"
          maxlength="2000"
          :disabled="loading"
          class="w-full rounded-lg border border-outline-variant bg-white/50 p-6 text-sm leading-relaxed text-on-surface outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 disabled:opacity-50 placeholder:text-outline"
          placeholder="在这里粘贴职位要求..."
          @input="emit('update:jobDescription', ($event.target as HTMLTextAreaElement).value)"
        ></textarea>
      </div>

      <!-- Resume Upload -->
      <div class="space-y-1.5">
        <label class="block font-mono text-xs font-semibold uppercase tracking-[0.05em] text-on-surface-variant">上传简历</label>
        <div
          class="group flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-outline-variant bg-surface-container-low p-6 transition-colors hover:bg-surface-container-high"
          :class="isDragOver ? 'border-primary bg-surface-container-high' : ''"
          @click="fileInputRef?.click()"
          @dragover.prevent="isDragOver = true"
          @dragleave.prevent="isDragOver = false"
          @drop.prevent="handleDrop"
        >
          <input ref="fileInputRef" class="hidden" type="file" accept="application/pdf,.pdf" :disabled="loading" @change="handleSelect" />
          <span
            class="material-symbols-outlined mb-3 text-4xl transition-colors"
            :class="isDragOver ? 'text-primary' : 'text-outline group-hover:text-primary'"
          >cloud_upload</span>
          <p class="text-sm font-semibold text-primary">点击上传或拖拽文件</p>
          <p class="text-sm text-on-surface-variant">上传简历可提高题目质量</p>
          <p class="mt-1 font-mono text-[11px] tracking-[0.05em] text-outline">{{ resumeFileName || 'PDF（最大 5MB）' }}</p>
        </div>
      </div>

      <!-- Error -->
      <p v-if="errorMessage" class="rounded-lg border border-error-container bg-error-container/50 px-4 py-3 text-sm text-on-error-container">{{ errorMessage }}</p>

      <!-- Ready Check & Submit -->
      <div class="border-t border-outline-variant/20 pt-6">
        <div class="flex flex-col gap-6 rounded-xl bg-surface-container-highest/30 p-6 md:flex-row md:items-center md:justify-between">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-secondary-container text-on-secondary-container">
              <span class="material-symbols-outlined" style="font-size:20px;">rocket_launch</span>
            </div>
            <div>
              <p class="text-sm font-bold text-on-surface">准备好开始了？</p>
              <p class="text-sm text-on-surface-variant">您的模拟面试大约需要 20 分钟。</p>
            </div>
          </div>
          <div class="flex shrink-0 items-center gap-3">
            <button
              type="button"
              class="h-10 rounded-lg border border-outline-variant bg-white/50 px-4 text-sm font-medium text-on-surface-variant transition-all hover:border-outline hover:bg-surface-container-high disabled:opacity-50"
              :disabled="loading"
              @click="emit('back')"
            >
              返回
            </button>
            <button
              type="submit"
              class="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-primary px-6 text-sm font-semibold text-on-primary shadow-md transition-all active:scale-95 hover:bg-primary-container disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="disableSubmit || loading"
            >
              {{ loading ? '生成中...' : '创建并开始面试' }}
              <span class="material-symbols-outlined" style="font-size:20px;">arrow_forward</span>
            </button>
          </div>
        </div>
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

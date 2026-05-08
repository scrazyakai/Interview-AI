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
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="pointer-events-none absolute right-4 top-3 text-outline" style="width:20px;height:20px;"><path d="M16.59 8.59 12 13.17 7.41 8.59 6 10l6 6 6-6z"></path></svg>
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
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="pointer-events-none absolute right-4 top-3 text-outline" style="width:20px;height:20px;"><path d="M16.59 8.59 12 13.17 7.41 8.59 6 10l6 6 6-6z"></path></svg>
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
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" class="pointer-events-none absolute right-4 top-3 text-outline" style="width:20px;height:20px;"><path d="M16.59 8.59 12 13.17 7.41 8.59 6 10l6 6 6-6z"></path></svg>
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
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            class="mb-3 transition-colors"
            style="width:36px;height:36px;"
            :class="isDragOver ? 'text-primary' : 'text-outline group-hover:text-primary'"
          ><path d="M19.35 10.04A7.49 7.49 0 0 0 12 4C9.11 4 6.6 5.64 5.35 8.04A5.994 5.994 0 0 0 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM19 18H6c-2.21 0-4-1.79-4-4 0-2.05 1.53-3.76 3.56-3.97l1.07-.11.5-.95A5.469 5.469 0 0 1 12 6c2.62 0 4.88 1.86 5.39 4.43l.3 1.5 1.53.11A2.98 2.98 0 0 1 22 15c0 1.65-1.35 3-3 3zM8 13h2.55v3h2.9v-3H16l-4-4z"/></svg>
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
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;"><path d="M6 15c-.83 0-1.58.34-2.12.88C2.7 17.06 2 22 2 22s4.94-.7 6.12-1.88A2.996 2.996 0 0 0 6 15zm.71 3.71c-.28.28-2.17.76-2.17.76s.47-1.88.76-2.17c.17-.19.42-.3.7-.3a1.003 1.003 0 0 1 .71 1.71zm10.71-5.06c6.36-6.36 4.24-11.31 4.24-11.31S16.71.22 10.35 6.58l-2.49-.5a2.03 2.03 0 0 0-1.81.55L2 10.69l5 2.14L11.17 17l2.14 5 4.05-4.05c.47-.47.68-1.15.55-1.81l-.49-2.49zM7.41 10.83l-1.91-.82 1.97-1.97 1.44.29c-.57.83-1.08 1.7-1.5 2.5zm6.58 7.67-.82-1.91c.8-.42 1.67-.93 2.49-1.5l.29 1.44-1.96 1.97zM16 12.24c-1.32 1.32-3.38 2.4-4.04 2.73l-2.93-2.93c.32-.65 1.4-2.71 2.73-4.04 4.68-4.68 8.23-3.99 8.23-3.99s.69 3.55-3.99 8.23zM15 11c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2z"/></svg>
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
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width:20px;height:20px;"><path d="m12 4-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z"></path></svg>
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

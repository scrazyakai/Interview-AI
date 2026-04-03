<template>
  <div class="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
    <div class="flex items-center gap-3">
      <div
        v-for="step in steps"
        :key="step.id"
        class="flex items-center gap-3"
      >
        <div
          class="flex h-9 w-9 items-center justify-center rounded-full text-sm font-semibold transition"
          :class="step.id <= current ? 'bg-yellow-500 text-white shadow' : 'bg-gray-100 text-gray-500'"
        >
          {{ step.id }}
        </div>
        <p class="text-sm font-medium" :class="step.id <= current ? 'text-gray-900' : 'text-gray-500'">
          {{ step.label }}
        </p>
        <div v-if="step.id < steps.length" class="h-px w-8 bg-gray-200"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    current?: number
  }>(),
  {
    current: 1,
  },
)

const steps = [
  { id: 1, label: '配置面试' },
  { id: 2, label: '开始面试' },
]
</script>

<template>
  <aside class="rounded-2xl border border-gray-100 bg-white p-6 shadow-md">
    <h3 class="text-xl font-semibold text-gray-900">🤖 AI 将为你生成</h3>
    <ul class="mt-5 space-y-3">
      <li v-for="item in highlights" :key="item" class="flex items-start gap-2 text-sm text-gray-700">
        <span class="mt-0.5 text-yellow-500">✔</span>
        <span>{{ item }}</span>
      </li>
    </ul>

    <div class="mt-6 rounded-xl border border-yellow-100 bg-yellow-50 p-4 text-sm text-yellow-800">
      {{ averageTip }}
    </div>
  </aside>
</template>

<script setup lang="ts">
defineProps<{
  highlights: string[]
  averageTip: string
}>()
</script>

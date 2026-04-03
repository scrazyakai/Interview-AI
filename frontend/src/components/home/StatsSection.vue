<template>
  <section class="px-4 py-8 sm:px-6 lg:px-8 lg:py-10">
    <div class="mx-auto grid max-w-7xl gap-4 rounded-2xl border border-[#eee8d8] bg-[#fbf8ef] px-6 py-8 sm:grid-cols-2 lg:grid-cols-4">
      <article v-for="item in stats" :key="item.value" class="text-center">
        <p class="text-4xl font-extrabold tracking-tight text-[#e0a40f]">{{ item.value }}</p>
        <p class="mt-2 text-sm text-[#757575]">{{ item.label }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { stats } from '../../mock/homeData'
</script>

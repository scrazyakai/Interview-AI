<template>
  <section class="px-4 py-16 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-7xl">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-[#1f1f1f] sm:text-4xl">
          他们如何斩获
          <span class="text-[#f5b61b]">心仪 Offer</span>
        </h2>
      </div>

      <div class="mt-10 grid gap-5 lg:grid-cols-3">
        <article
          v-for="item in testimonials"
          :key="item.name"
          class="rounded-2xl border border-[#ececec] bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
        >
          <div class="flex items-center gap-3">
            <div class="h-11 w-11 rounded-full bg-[linear-gradient(135deg,#f7d272,#f2b116)]"></div>
            <div>
              <p class="font-semibold text-[#2c2c2c]">{{ item.name }}</p>
              <p class="text-xs text-[#8a8a8a]">{{ item.role }}</p>
            </div>
          </div>
          <p class="mt-4 text-sm leading-6 text-[#5f5f5f]">“{{ item.quote }}”</p>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { testimonials } from '../../mock/homeData'
</script>

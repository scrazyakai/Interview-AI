<template>
  <section class="px-4 py-16 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-4xl">
      <div class="text-center">
        <h2 class="text-3xl font-bold text-[#1f1f1f] sm:text-4xl">常见问题</h2>
        <p class="mt-3 text-sm text-[#848484]">解答你关于模拟面试的疑问，帮助你更好了解服务。</p>
      </div>

      <div class="mt-8 space-y-3">
        <article
          v-for="(item, index) in faqs"
          :key="item.q"
          class="overflow-hidden rounded-2xl border border-[#ece8dc] bg-white transition hover:border-[#f2d27a]"
        >
          <button
            type="button"
            class="flex w-full items-center justify-between px-5 py-4 text-left"
            @click="toggle(index)"
          >
            <span class="text-sm font-semibold text-[#2f2f2f] sm:text-base">{{ item.q }}</span>
            <span
              class="ml-3 inline-flex h-6 w-6 items-center justify-center rounded-full bg-[#fff5dd] text-[#b98200] transition"
              :class="activeIndex === index ? 'rotate-180' : ''"
            >
              +
            </span>
          </button>

          <transition
            enter-active-class="transition duration-300 ease-out"
            enter-from-class="max-h-0 opacity-0"
            enter-to-class="max-h-48 opacity-100"
            leave-active-class="transition duration-200 ease-in"
            leave-from-class="max-h-48 opacity-100"
            leave-to-class="max-h-0 opacity-0"
          >
            <div v-if="activeIndex === index" class="px-5 pb-5 text-sm leading-7 text-[#666]">
              {{ item.a }}
            </div>
          </transition>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { faqs } from '../../mock/homeData'

const activeIndex = ref(0)

function toggle(index: number) {
  activeIndex.value = activeIndex.value === index ? -1 : index
}
</script>

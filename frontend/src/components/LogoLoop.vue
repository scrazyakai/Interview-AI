<template>
  <div class="logo-loop-wrapper">
    <div class="logo-loop-track">
      <div class="logo-loop-list">
        <slot />
      </div>
      <div class="logo-loop-list" aria-hidden="true">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  duration?: number
}>()
</script>

<style scoped>
.logo-loop-wrapper {
  overflow: hidden;
  width: 100%;
  mask-image: linear-gradient(to right, transparent 0%, black 10%, black 90%, transparent 100%);
  -webkit-mask-image: linear-gradient(to right, transparent 0%, black 10%, black 90%, transparent 100%);
}

.logo-loop-track {
  display: flex;
  width: max-content;
  animation: logo-marquee 28s linear infinite;
}

.logo-loop-track:hover {
  animation-play-state: paused;
}

.logo-loop-list {
  display: flex;
  align-items: center;
  gap: 4rem;
  padding: 0 2rem;
}

@keyframes logo-marquee {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}
</style>

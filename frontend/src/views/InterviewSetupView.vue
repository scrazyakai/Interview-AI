<script setup lang="ts">
import InterviewSetupPage from './InterviewSetupPage.vue'
</script>

<template>
  <div class="min-h-screen bg-background">
    <!-- Ambient gradient background -->
    <div
      class="pointer-events-none fixed inset-0 z-0"
      style="
        background: radial-gradient(ellipse at 15% 20%, rgba(0, 35, 111, 0.08) 0%, transparent 55%),
                    radial-gradient(ellipse at 85% 80%, rgba(0, 108, 73, 0.06) 0%, transparent 50%),
                    #f8f9ff;
      "
    ></div>
    <div class="relative z-10">
      <InterviewSetupPage />
    </div>
  </div>
</template>

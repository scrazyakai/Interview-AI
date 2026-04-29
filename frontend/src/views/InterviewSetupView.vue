<script setup lang="ts">
import { useRouter } from 'vue-router'

import AppTopbar from '../components/AppTopbar.vue'
import { clearAuthSession } from '../utils/auth'
import InterviewSetupPage from './InterviewSetupPage.vue'

const router = useRouter()

function logout() {
  clearAuthSession()
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-white">
    <div class="px-4 pb-2 pt-4 sm:px-6 lg:px-8">
      <AppTopbar @logout="logout" />
    </div>
    <InterviewSetupPage />
  </div>
</template>

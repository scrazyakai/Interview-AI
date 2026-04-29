<script setup lang="ts">
import { useRouter } from 'vue-router'

import AppTopbar from '../components/AppTopbar.vue'
import { clearAuthSession } from '../utils/auth'
import AboutPage from './AboutPage.vue'

const router = useRouter()

function logout() {
  clearAuthSession()
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen bg-[#f7f3eb]">
    <div class="px-4 pb-2 pt-4 sm:px-6 lg:px-8">
      <AppTopbar @logout="logout" />
    </div>
    <AboutPage />
  </div>
</template>

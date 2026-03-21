<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import AppTopbar from '../components/AppTopbar.vue'
import { clearAuthSession, loadAuthSession, type TokenResponse } from '../utils/auth'

const router = useRouter()
const session = ref<TokenResponse | null>(loadAuthSession())

function logout() {
  clearAuthSession()
  session.value = null
  router.push('/')
}
</script>

<template>
  <main class="landing-page">
    <AppTopbar :session="session" @logout="logout" />

    <section class="hero-shell">
      <section class="profile-card" style="padding: 32px; margin-top: 24px;">
        <p class="profile-kicker">&#20851;&#20110;</p>
        <h1 style="margin-top: 16px; color: #111827;">About</h1>
        <p class="profile-subtitle">
          &#36825;&#20010;&#39029;&#38754;&#24050;&#32463;&#20351;&#29992;&#19982;&#20027;&#39029;&#19968;&#33268;&#30340;&#23548;&#33322;&#26639;&#32452;&#20214;&#12290;
        </p>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppTopbar from './components/AppTopbar.vue'

const route = useRoute()
const showTopbar = computed(() => route.path !== '/interview')
</script>

<template>
  <AppTopbar v-if="showTopbar" />
  <RouterView />
</template>

<template>
  <main class="bg-[#f8f8f6] text-[#1f1f1f]">
    <HeroSection @start="handleHeroStart" />
    <FeatureCards />
    <StatsSection />
    <WhyChooseUs />
    <TestimonialsSection />
    <FaqSection />
    <CtaSection />
    <SimpleFooter />
  </main>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

import HeroSection from '../components/home/HeroSection.vue'
import FeatureCards from '../components/home/FeatureCards.vue'
import StatsSection from '../components/home/StatsSection.vue'
import WhyChooseUs from '../components/home/WhyChooseUs.vue'
import TestimonialsSection from '../components/home/TestimonialsSection.vue'
import FaqSection from '../components/home/FaqSection.vue'
import CtaSection from '../components/home/CtaSection.vue'
import SimpleFooter from '../components/home/SimpleFooter.vue'
import type { ExperienceLevelValue } from '../constants/interviewOptions'

const router = useRouter()

function handleHeroStart(payload: { jobTitle: string; experienceLevel: ExperienceLevelValue }) {
  router.push({
    path: '/interview/setup',
    query: {
      job_title: payload.jobTitle,
      experience_level: payload.experienceLevel,
    },
  })
}
</script>

<script setup lang="ts">
import { onMounted } from 'vue'
import AppHeader from './components/layout/AppHeader.vue'
import AppFooter from './components/layout/AppFooter.vue'
import { useAuth } from './composables/useAuth'

const { fetchUser } = useAuth()

onMounted(() => {
  fetchUser()
})
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <a href="#main-content" class="skip-link">Przejdź do treści</a>
    <AppHeader />
    <main id="main-content" class="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>

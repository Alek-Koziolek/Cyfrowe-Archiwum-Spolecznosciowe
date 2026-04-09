<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { listPhotos } from '../api/photos'
import type { Photo } from '../types/photo'
import PhotoCard from '../components/photo/PhotoCard.vue'

const recentPhotos = ref<Photo[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const result = await listPhotos(1, 8)
    recentPhotos.value = result.items
  } catch {
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <section class="text-center py-16">
      <h1 class="text-4xl md:text-5xl font-bold text-[var(--color-on-bg)] mb-4">
        Cyfrowe Archiwum Społecznościowe
      </h1>
      <p class="text-lg text-[var(--color-on-surface)] max-w-2xl mx-auto mb-8">
        Odkryj historię swojego otoczenia. Przeglądaj i udostępniaj zdjęcia dokumentujące przemiany miejsc, które znasz.
      </p>
      <div class="flex gap-4 justify-center flex-wrap">
        <RouterLink to="/browse"
          class="px-6 py-3 rounded-lg bg-[var(--color-primary)] text-[var(--color-on-primary)] font-medium no-underline hover:bg-[var(--color-primary-hover)] transition-colors">
          Przeglądaj archiwum
        </RouterLink>
        <RouterLink to="/search"
          class="px-6 py-3 rounded-lg border border-[var(--color-border)] text-[var(--color-on-surface)] font-medium no-underline hover:border-[var(--color-primary)] transition-colors">
          Szukaj zdjęć
        </RouterLink>
      </div>
    </section>
    <section v-if="!loading && recentPhotos.length > 0" aria-label="Ostatnio dodane zdjęcia">
      <h2 class="text-2xl font-semibold text-[var(--color-on-bg)] mb-6">
        Ostatnio dodane
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <PhotoCard v-for="photo in recentPhotos" :key="photo.id" :photo="photo" />
      </div>
    </section>
    <div v-if="loading" class="text-center py-12 text-[var(--color-muted)]" role="status">
      Ładowanie...
    </div>
  </div>
</template>

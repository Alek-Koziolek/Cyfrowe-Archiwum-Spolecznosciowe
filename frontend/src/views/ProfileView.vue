<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import { listMyPhotos } from '../api/photos'
import type { Photo } from '../types/photo'
import PhotoCard from '../components/photo/PhotoCard.vue'

const { user } = useAuth()
const myPhotos = ref<Photo[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const result = await listMyPhotos(1, 50)
    myPhotos.value = result.items
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-[var(--color-on-bg)] mb-2">Mój profil</h1>
    <p class="text-[var(--color-on-surface)] mb-6">
      {{ user?.display_name }} &middot; {{ user?.email }}
    </p>

    <h2 class="text-xl font-semibold text-[var(--color-on-bg)] mb-4">Moje zdjęcia</h2>
    <div v-if="loading" class="text-[var(--color-muted)]" role="status">Ładowanie...</div>
    <div v-else-if="myPhotos.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <PhotoCard v-for="photo in myPhotos" :key="photo.id" :photo="photo" />
    </div>
    <p v-else class="text-[var(--color-muted)]">Nie dodałeś jeszcze żadnych zdjęć.</p>
  </div>
</template>

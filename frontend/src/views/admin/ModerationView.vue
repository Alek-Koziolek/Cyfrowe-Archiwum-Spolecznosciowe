<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/client'
import { adminDeletePhoto } from '../../api/admin'
import { thumbnailUrl } from '../../api/photos'
import type { Photo } from '../../types/photo'
import PhotoEditModal from '../../components/admin/PhotoEditModal.vue'
import ConfirmModal from '../../components/common/ConfirmModal.vue'

const photos = ref<Photo[]>([])
const loading = ref(true)
const editingPhoto = ref<Photo | null>(null)
const photoToDelete = ref<Photo | null>(null)

onMounted(async () => {
  const res = await api.get('/photos', { params: { page: 1, per_page: 50 } })
  photos.value = res.data.items
  loading.value = false
})

async function handleDelete(photo: Photo) {
  photoToDelete.value = photo
}

async function onConfirmDelete() {
  if (!photoToDelete.value) return
  const photo = photoToDelete.value
  photoToDelete.value = null
  await adminDeletePhoto(photo.id)
  photos.value = photos.value.filter((p) => p.id !== photo.id)
}

function handleSaved(updated: Photo) {
  const idx = photos.value.findIndex(p => p.id === updated.id)
  if (idx !== -1) photos.value[idx] = updated
  editingPhoto.value = null
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-[var(--color-on-bg)] mb-6">Moderacja zdjęć</h1>

    <div v-if="loading" class="text-[var(--color-muted)]" role="status">Ładowanie...</div>
    <div v-else-if="photos.length > 0" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div v-for="photo in photos" :key="photo.id"
        class="rounded-lg border border-[var(--color-border)] overflow-hidden">
        <div class="aspect-[4/3] bg-[var(--color-surface)]">
          <img :src="thumbnailUrl(photo.id)" :alt="photo.title" class="w-full h-full object-cover" loading="lazy" />
        </div>
        <div class="p-3">
          <h3 class="text-sm font-semibold text-[var(--color-on-bg)] truncate">{{ photo.title }}</h3>
          <p class="text-xs text-[var(--color-muted)]">Autor: {{ photo.owner.display_name }}</p>
          <div class="mt-2 flex gap-2">
            <button
              class="px-3 py-1 rounded text-sm bg-[var(--color-primary)] text-[var(--color-on-primary)] cursor-pointer"
              :aria-label="`Edytuj zdjęcie ${photo.title}`" @click="editingPhoto = photo">
              Edytuj
            </button>
            <button
              class="px-3 py-1 rounded text-sm bg-[var(--color-error)] text-[var(--color-on-error)] cursor-pointer"
              :aria-label="`Usuń zdjęcie ${photo.title}`" @click="handleDelete(photo)">
              Usuń
            </button>
          </div>
        </div>
      </div>
    </div>
    <p v-else class="text-[var(--color-muted)]">Brak zdjęć do moderacji.</p>

    <PhotoEditModal v-if="editingPhoto" :photo="editingPhoto" @saved="handleSaved" @close="editingPhoto = null" />

    <ConfirmModal v-if="photoToDelete" :message="`Usunąć zdjęcie &quot;${photoToDelete.title}&quot;?`"
      confirm-label="Usuń" @confirm="onConfirmDelete" @cancel="photoToDelete = null" />
  </div>
</template>

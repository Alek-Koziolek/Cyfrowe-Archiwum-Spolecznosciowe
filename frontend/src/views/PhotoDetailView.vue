<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPhoto, fullImageUrl, deletePhoto } from '../api/photos'
import { adminDeletePhoto, toggleBlockUser } from '../api/admin'
import { useAuth } from '../composables/useAuth'
import PhotoEditModal from '../components/admin/PhotoEditModal.vue'
import ConfirmModal from '../components/common/ConfirmModal.vue'
import PhotoDate from '../components/photo/PhotoDate.vue'
import type { Photo } from '../types/photo'

const route = useRoute()
const router = useRouter()
const { user } = useAuth()

const photo = ref<Photo | null>(null)
const loading = ref(true)
const error = ref('')
const editingPhoto = ref<Photo | null>(null)
const confirmState = ref<{ message: string; onConfirm: () => Promise<void> } | null>(null)

const isOwner = () => photo.value && user.value && photo.value.owner.id === user.value.id
const isAdmin = () => user.value?.role === 'admin'

onMounted(async () => {
  try {
    photo.value = await getPhoto(Number(route.params.id))
  } catch {
    error.value = 'Nie znaleziono zdjęcia.'
  } finally {
    loading.value = false
  }
})

function handleDelete() {
  if (!photo.value) return
  confirmState.value = {
    message: 'Czy na pewno chcesz usunąć to zdjęcie?',
    onConfirm: async () => {
      if (isAdmin()) {
        await adminDeletePhoto(photo.value!.id)
      } else {
        await deletePhoto(photo.value!.id)
      }
      router.push('/')
    },
  }
}

function handleToggleBlock() {
  if (!photo.value) return
  const owner = photo.value.owner
  const action = owner.is_blocked ? 'odblokować' : 'zablokować'
  confirmState.value = {
    message: `Czy na pewno chcesz ${action} użytkownika ${owner.display_name}?`,
    onConfirm: async () => {
      const updated = await toggleBlockUser(owner.id)
      photo.value = { ...photo.value!, owner: { ...owner, is_blocked: updated.is_blocked } }
    },
  }
}

async function onConfirm() {
  const state = confirmState.value
  confirmState.value = null
  await state?.onConfirm()
}
</script>

<template>
  <div v-if="loading" class="text-[var(--color-muted)]" role="status">Ładowanie...</div>
  <div v-else-if="error" class="text-[var(--color-error)]">{{ error }}</div>
  <article v-else-if="photo" class="max-w-4xl mx-auto">
    <img :src="fullImageUrl(photo.id)" :alt="photo.title" class="w-full rounded-lg mb-6" />

    <h1 class="text-3xl font-bold text-[var(--color-on-bg)] mb-2">{{ photo.title }}</h1>

    <div class="flex gap-4 flex-wrap text-sm text-[var(--color-muted)] mb-4">
      <span v-if="photo.location_text">{{ photo.location_text }}</span>
      <PhotoDate :date-taken="photo.date_taken" :date-precision="photo.date_precision" />
      <span>Dodane przez: {{ photo.owner.display_name }}</span>
    </div>

    <p v-if="photo.description" class="text-[var(--color-on-surface)] mb-4">
      {{ photo.description }}
    </p>

    <div v-if="photo.tags.length > 0" class="flex gap-2 flex-wrap mb-6">
      <button v-for="tag in photo.tags" :key="tag"
        class="px-2 py-1 rounded-full text-xs bg-[var(--color-surface)] text-[var(--color-on-surface)] border border-[var(--color-border)] cursor-pointer hover:opacity-75 transition-opacity"
        @click="router.push({ name: 'search', query: { tag } })">
        {{ tag }}
      </button>
    </div>

    <div v-if="photo.hierarchy_node" class="text-sm text-[var(--color-muted)] mb-6">
      Lokalizacja:
      <span v-if="photo.hierarchy_node.parent">{{ photo.hierarchy_node.name }}, {{ photo.hierarchy_node.parent.name
        }}</span>
      <span v-else>{{ photo.hierarchy_node.name }}</span>
    </div>

    <div v-if="isOwner() || isAdmin()" class="flex gap-3 flex-wrap">
      <button class="px-4 py-2 rounded-md bg-[var(--color-primary)] text-[var(--color-on-primary)] cursor-pointer"
        @click="editingPhoto = photo">
        Edytuj zdjęcie
      </button>
      <button class="px-4 py-2 rounded-md bg-[var(--color-error)] text-[var(--color-on-error)] cursor-pointer"
        @click="handleDelete">
        Usuń zdjęcie
      </button>
      <button v-if="isAdmin() && !isOwner()" class="px-4 py-2 rounded-md cursor-pointer" :class="photo.owner.is_blocked
        ? 'bg-[var(--color-surface)] text-[var(--color-on-surface)] border border-[var(--color-border)]'
        : 'bg-yellow-600 text-white'" @click="handleToggleBlock">
        {{ photo.owner.is_blocked ? 'Odblokuj autora' : 'Zablokuj autora' }}
      </button>
    </div>

    <PhotoEditModal v-if="editingPhoto" :photo="editingPhoto" :is-admin="isAdmin()"
      @saved="(updated) => { photo = updated; editingPhoto = null }" @close="editingPhoto = null" />

    <ConfirmModal v-if="confirmState" :message="confirmState.message" confirm-label="Potwierdź" @confirm="onConfirm"
      @cancel="confirmState = null" />
  </article>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/client'
import type { HierarchyNode, HierarchyNodeWithChildren } from '../types/hierarchy'
import type { Photo } from '../types/photo'
import PhotoCard from '../components/photo/PhotoCard.vue'

const rootNodes = ref<HierarchyNode[]>([])
const currentNode = ref<HierarchyNodeWithChildren | null>(null)
const breadcrumb = ref<HierarchyNode[]>([])
const photos = ref<Photo[]>([])
const loading = ref(true)

async function loadRoots() {
  const res = await api.get<HierarchyNode[]>('/hierarchy')
  rootNodes.value = res.data
  loading.value = false
}

async function selectNode(node: HierarchyNode) {
  loading.value = true
  const res = await api.get<HierarchyNodeWithChildren>(`/hierarchy/${node.id}`)
  currentNode.value = res.data
  breadcrumb.value = [...breadcrumb.value, node]

  const photosRes = await api.get(`/search?node_id=${node.id}`)
  photos.value = photosRes.data.items
  loading.value = false
}

function goBack(index: number) {
  if (index < 0) {
    currentNode.value = null
    breadcrumb.value = []
    photos.value = []
    return
  }
  breadcrumb.value = breadcrumb.value.slice(0, index + 1)
  selectNode(breadcrumb.value[index])
  breadcrumb.value = breadcrumb.value.slice(0, index)
}

onMounted(loadRoots)
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-[var(--color-on-bg)] mb-6">Przeglądaj archiwum</h1>

    <nav aria-label="Ścieżka" class="mb-6 flex gap-2 items-center text-sm flex-wrap">
      <button class="text-[var(--color-primary)] hover:underline cursor-pointer" @click="goBack(-1)">
        Start
      </button>
      <template v-for="(node, i) in breadcrumb" :key="node.id">
        <span class="text-[var(--color-muted)]">/</span>
        <button class="text-[var(--color-primary)] hover:underline cursor-pointer" @click="goBack(i)">
          {{ node.name }}
        </button>
      </template>
    </nav>

    <div class="grid grid-cols-1 lg:grid-cols-[300px_1fr] gap-8">
      <aside>
        <h2 class="text-lg font-semibold text-[var(--color-on-bg)] mb-3">
          {{ currentNode ? 'Podkategorie' : 'Województwa' }}
        </h2>
        <ul class="space-y-1" role="list">
          <li v-for="node in (currentNode?.children || rootNodes)" :key="node.id">
            <button
              class="w-full text-left px-3 py-2 rounded-md hover:bg-[var(--color-surface)] text-[var(--color-on-surface)] cursor-pointer transition-colors"
              @click="selectNode(node)">
              {{ node.name }}
            </button>
          </li>
          <li v-if="(currentNode?.children || rootNodes).length === 0" class="text-[var(--color-muted)] text-sm px-3">
            Brak podkategorii
          </li>
        </ul>
      </aside>
      <section aria-label="Zdjęcia">
        <div v-if="loading" class="text-[var(--color-muted)]" role="status">Ładowanie...</div>
        <div v-else-if="photos.length > 0" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
          <PhotoCard v-for="photo in photos" :key="photo.id" :photo="photo" />
        </div>
        <p v-else class="text-[var(--color-muted)]">
          {{ currentNode ? 'Brak zdjęć w tej kategorii.' : 'Wybierz lokalizację, aby zobaczyć zdjęcia.' }}
        </p>
      </section>
    </div>
  </div>
</template>

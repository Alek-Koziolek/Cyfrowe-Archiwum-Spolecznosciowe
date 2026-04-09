<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/client'
import type { Photo } from '../types/photo'
import type { HierarchyNode } from '../types/hierarchy'
import PhotoCard from '../components/photo/PhotoCard.vue'

const route = useRoute()
const query = ref('')
const activeTags = ref<string[]>([])
const dateFrom = ref('')
const dateTo = ref('')
const photos = ref<Photo[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)

const wojewodztwa = ref<HierarchyNode[]>([])
const selectedWojewodztwoId = ref<number | null>(null)
const miastoInput = ref('')
const selectedMiastoId = ref<number | null>(null)
const miastoSuggestions = ref<HierarchyNode[]>([])
const showSuggestions = ref(false)
const focusedMiastoIndex = ref(-1)
let suggestTimer: ReturnType<typeof setTimeout> | null = null

const tagInput = ref('')
const tagSuggestions = ref<string[]>([])
const showTagSuggestions = ref(false)
const focusedTagIndex = ref(-1)
let tagSuggestTimer: ReturnType<typeof setTimeout> | null = null

const activeNodeId = computed(() => selectedMiastoId.value ?? selectedWojewodztwoId.value)

onMounted(async () => {
  const res = await api.get<HierarchyNode[]>('/hierarchy')
  wojewodztwa.value = res.data
  if (route.query.tag) {
    const tagParam = route.query.tag
    activeTags.value = Array.isArray(tagParam) ? (tagParam as string[]) : [tagParam as string]
    search()
  }
})

watch(() => route.query.tag, (newTag) => {
  if (!newTag) {
    activeTags.value = []
  } else if (Array.isArray(newTag)) {
    activeTags.value = newTag as string[]
  } else {
    activeTags.value = [newTag as string]
  }
  page.value = 1
  search()
})

function onWojewodztwoChange(id: string) {
  selectedWojewodztwoId.value = id ? Number(id) : null
  miastoInput.value = ''
  selectedMiastoId.value = null
  miastoSuggestions.value = []
  focusedMiastoIndex.value = -1
}

async function onMiastoInput() {
  selectedMiastoId.value = null
  focusedMiastoIndex.value = -1
  if (!selectedWojewodztwoId.value) return
  if (suggestTimer) clearTimeout(suggestTimer)
  suggestTimer = setTimeout(async () => {
    const res = await api.get<HierarchyNode[]>(
      `/hierarchy/${selectedWojewodztwoId.value}/children?q=${encodeURIComponent(miastoInput.value)}`
    )
    miastoSuggestions.value = res.data
    showSuggestions.value = true
  }, 250)
}

function selectMiasto(node: HierarchyNode) {
  miastoInput.value = node.name
  selectedMiastoId.value = node.id
  showSuggestions.value = false
  focusedMiastoIndex.value = -1
}

function onMiastoBlur() {
  setTimeout(() => { showSuggestions.value = false; focusedMiastoIndex.value = -1 }, 150)
}

function onMiastoKeydown(e: KeyboardEvent) {
  if (!showSuggestions.value) return
  const total = miastoSuggestions.value.length
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    focusedMiastoIndex.value = Math.min(focusedMiastoIndex.value + 1, total - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    focusedMiastoIndex.value = Math.max(focusedMiastoIndex.value - 1, -1)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (focusedMiastoIndex.value >= 0 && focusedMiastoIndex.value < total) {
      selectMiasto(miastoSuggestions.value[focusedMiastoIndex.value])
    }
  } else if (e.key === 'Escape') {
    showSuggestions.value = false
    focusedMiastoIndex.value = -1
  }
}

const exactMiastoMatch = computed(() =>
  miastoSuggestions.value.some(n => n.name.toLowerCase() === miastoInput.value.toLowerCase())
)

let debounceTimer: ReturnType<typeof setTimeout>

async function search() {
  loading.value = true
  const params: Record<string, string | number | string[]> = { page: page.value, per_page: 20 }
  if (query.value) params.q = query.value
  if (dateFrom.value) params.date_from = dateFrom.value
  if (dateTo.value) params.date_to = dateTo.value
  if (activeNodeId.value) params.node_id = activeNodeId.value
  if (activeTags.value.length > 0) params['tags'] = activeTags.value

  try {
    const res = await api.get('/search', { params })
    photos.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

watch(query, () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    search()
  }, 300)
})

function applyFilters() {
  page.value = 1
  search()
}

async function onTagInput() {
  if (tagSuggestTimer) clearTimeout(tagSuggestTimer)
  tagSuggestTimer = setTimeout(async () => {
    if (tagInput.value.trim().length < 2) {
      tagSuggestions.value = []
      showTagSuggestions.value = false
      return
    }
    const res = await api.get<{ suggestions: string[] }>('/search/suggest', {
      params: { q: tagInput.value, tags_only: true },
    })
    tagSuggestions.value = res.data.suggestions.filter((s) => !activeTags.value.includes(s))
    showTagSuggestions.value = true
  }, 250)
}

function selectTag(tag: string) {
  if (!activeTags.value.includes(tag)) activeTags.value.push(tag)
  tagInput.value = ''
  tagSuggestions.value = []
  showTagSuggestions.value = false
  focusedTagIndex.value = -1
  page.value = 1
  search()
}

function removeTag(tag: string) {
  activeTags.value = activeTags.value.filter((t) => t !== tag)
  page.value = 1
  search()
}

function onTagBlur() {
  setTimeout(() => { showTagSuggestions.value = false; focusedTagIndex.value = -1 }, 150)
}

function onTagKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !showTagSuggestions.value) return
  const total = tagSuggestions.value.length
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    showTagSuggestions.value = true
    focusedTagIndex.value = Math.min(focusedTagIndex.value + 1, total - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    focusedTagIndex.value = Math.max(focusedTagIndex.value - 1, -1)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (focusedTagIndex.value >= 0 && focusedTagIndex.value < total) {
      selectTag(tagSuggestions.value[focusedTagIndex.value])
    } else if (tagInput.value.trim()) {
      selectTag(tagInput.value.trim())
    }
  } else if (e.key === 'Escape') {
    showTagSuggestions.value = false
    focusedTagIndex.value = -1
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-[var(--color-on-bg)] mb-6">Szukaj zdjęć</h1>

    <div class="mb-6">
      <label for="search" class="sr-only">Wyszukaj</label>
      <input id="search" v-model="query" type="search" placeholder="Szukaj po nazwie, opisie, lokalizacji..."
        class="w-full px-4 py-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)] text-lg" />
    </div>

    <div class="flex gap-4 mb-6 flex-wrap items-end">
      <div>
        <label for="filterWojewodztwo" class="block text-sm text-[var(--color-on-surface)] mb-1">Województwo</label>
        <select id="filterWojewodztwo" :value="selectedWojewodztwoId ?? ''"
          @change="onWojewodztwoChange(($event.target as HTMLSelectElement).value)"
          class="px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]">
          <option value="">— wszystkie —</option>
          <option v-for="node in wojewodztwa" :key="node.id" :value="node.id">{{ node.name }}</option>
        </select>
      </div>

      <div v-if="selectedWojewodztwoId" class="relative">
        <label for="filterMiasto" class="block text-sm text-[var(--color-on-surface)] mb-1">Miasto / Gmina</label>
        <input id="filterMiasto" v-model="miastoInput" type="text" autocomplete="off"
          placeholder="Filtruj po miejscowości…" role="combobox" aria-haspopup="listbox"
          :aria-expanded="showSuggestions && miastoSuggestions.length > 0" aria-controls="search-miasto-listbox"
          aria-autocomplete="list"
          :aria-activedescendant="focusedMiastoIndex >= 0 ? `search-miasto-option-${focusedMiastoIndex}` : undefined"
          class="px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]"
          @input="onMiastoInput" @focus="onMiastoInput" @blur="onMiastoBlur" @keydown="onMiastoKeydown" />
        <ul v-if="showSuggestions && miastoSuggestions.length > 0" id="search-miasto-listbox"
          class="absolute z-10 w-full mt-1 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] shadow-md max-h-52 overflow-y-auto"
          role="listbox">
          <li v-for="(node, i) in miastoSuggestions" :key="node.id" :id="`search-miasto-option-${i}`" role="option"
            :aria-selected="i === focusedMiastoIndex"
            :class="['px-3 py-2 cursor-pointer text-[var(--color-on-surface)]', i === focusedMiastoIndex ? 'bg-[var(--color-bg)]' : 'hover:bg-[var(--color-bg)]']"
            @mousedown.prevent="selectMiasto(node)">
            {{ node.name }}
          </li>
          <li v-if="miastoInput.trim() && !exactMiastoMatch" class="px-3 py-2 text-[var(--color-muted)] italic text-sm"
            aria-hidden="true">
            Brak wyników dla „{{ miastoInput.trim() }}"
          </li>
        </ul>
      </div>

      <div>
        <label for="dateFrom" class="block text-sm text-[var(--color-on-surface)] mb-1">Od</label>
        <input id="dateFrom" v-model="dateFrom" type="text" placeholder="np. 1990"
          class="px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
      </div>
      <div>
        <label for="dateTo" class="block text-sm text-[var(--color-on-surface)] mb-1">Do</label>
        <input id="dateTo" v-model="dateTo" type="text" placeholder="np. 2024"
          class="px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
      </div>
      <div class="relative">
        <label for="filterTag" class="block text-sm text-[var(--color-on-surface)] mb-1">Tagi</label>
        <input id="filterTag" v-model="tagInput" type="text" autocomplete="off" placeholder="Dodaj tag…" role="combobox"
          aria-haspopup="listbox" :aria-expanded="showTagSuggestions && tagSuggestions.length > 0"
          aria-controls="tag-listbox" aria-autocomplete="list"
          :aria-activedescendant="focusedTagIndex >= 0 ? `tag-option-${focusedTagIndex}` : undefined"
          class="px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]"
          @input="onTagInput" @focus="onTagInput" @blur="onTagBlur" @keydown="onTagKeydown" />
        <ul v-if="showTagSuggestions && tagSuggestions.length > 0" id="tag-listbox"
          class="absolute z-10 w-full mt-1 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] shadow-md max-h-52 overflow-y-auto"
          role="listbox">
          <li v-for="(tag, i) in tagSuggestions" :key="tag" :id="`tag-option-${i}`" role="option"
            :aria-selected="i === focusedTagIndex"
            :class="['px-3 py-2 cursor-pointer text-[var(--color-on-surface)]', i === focusedTagIndex ? 'bg-[var(--color-bg)]' : 'hover:bg-[var(--color-bg)]']"
            @mousedown.prevent="selectTag(tag)">{{ tag }}</li>
        </ul>
      </div>

      <button class="px-4 py-2 rounded-md bg-[var(--color-primary)] text-[var(--color-on-primary)] cursor-pointer"
        @click="applyFilters">
        Filtruj
      </button>
    </div>

    <div v-if="activeTags.length > 0" class="flex flex-wrap gap-2 mb-4">
      <span v-for="tag in activeTags" :key="tag"
        class="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-[var(--color-surface)] text-[var(--color-on-surface)] border border-[var(--color-border)]">
        {{ tag }}
        <button type="button"
          class="text-[var(--color-muted)] hover:text-[var(--color-on-surface)] cursor-pointer leading-none"
          @click="removeTag(tag)" :aria-label="`Usuń tag ${tag}`">×</button>
      </span>
    </div>

    <div v-if="loading" class="text-[var(--color-muted)]" role="status">Wyszukiwanie...</div>
    <div v-else-if="photos.length > 0">
      <p class="text-sm text-[var(--color-muted)] mb-4" aria-live="polite">
        Znaleziono {{ total }} wyników
      </p>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <PhotoCard v-for="photo in photos" :key="photo.id" :photo="photo" />
      </div>
    </div>
    <p v-else-if="query || dateFrom || dateTo || activeNodeId || activeTags.length" class="text-[var(--color-muted)]">
      Brak wyników dla podanych kryteriów.
    </p>
    <p v-else class="text-[var(--color-muted)]">
      Wpisz frazę lub wybierz filtry, aby rozpocząć wyszukiwanie.
    </p>
  </div>
</template>
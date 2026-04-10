<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { maskDateInput, displayToIso } from '../utils/date'
import { useRouter } from 'vue-router'
import { uploadPhoto } from '../api/photos'
import api from '../api/client'
import type { HierarchyNode } from '../types/hierarchy'

const router = useRouter()

const title = ref('')
const description = ref('')
const dateTaken = ref('')
const datePrecision = ref<'year' | 'month' | 'day'>('day')
const locationText = ref('')
const tags = ref('')
const file = ref<File | null>(null)
const preview = ref<string | null>(null)
const errors = ref<Record<string, string>>({})
const loading = ref(false)

const wojewodztwa = ref<HierarchyNode[]>([])
const selectedWojewodztwoId = ref<number | null>(null)

const miastoInput = ref('')
const selectedMiastoId = ref<number | null>(null)
const miastoSuggestions = ref<HierarchyNode[]>([])
const showSuggestions = ref(false)
const focusedMiastoIndex = ref(-1)
let suggestTimer: ReturnType<typeof setTimeout> | null = null

const datePlaceholder = computed(() => {
  if (datePrecision.value === 'day') return 'DD.MM.RRRR'
  if (datePrecision.value === 'month') return 'MM.RRRR'
  return 'RRRR'
})

watch(datePrecision, () => { dateTaken.value = '' })

function handleDateInput(e: Event) {
  dateTaken.value = maskDateInput((e.target as HTMLInputElement).value, datePrecision.value)
}

function slugify(name: string): string {
  const map: Record<string, string> = {
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
    'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
  }
  return name.toLowerCase().replace(/[ąćęłńóśźż]/g, ch => map[ch] ?? ch).replace(/\s+/g, '-')
}

onMounted(async () => {
  const res = await api.get<HierarchyNode[]>('/hierarchy')
  wojewodztwa.value = res.data
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

function selectNewMiasto() {
  selectedMiastoId.value = null
  showSuggestions.value = false
  focusedMiastoIndex.value = -1
}

function onMiastoBlur() {
  setTimeout(() => { showSuggestions.value = false; focusedMiastoIndex.value = -1 }, 150)
}

function onMiastoKeydown(e: KeyboardEvent) {
  if (!showSuggestions.value) return
  const hasNew = !!miastoInput.value.trim() && !exactMiastoMatch.value
  const total = miastoSuggestions.value.length + (hasNew ? 1 : 0)
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    focusedMiastoIndex.value = Math.min(focusedMiastoIndex.value + 1, total - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    focusedMiastoIndex.value = Math.max(focusedMiastoIndex.value - 1, -1)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (focusedMiastoIndex.value >= 0 && focusedMiastoIndex.value < miastoSuggestions.value.length) {
      selectMiasto(miastoSuggestions.value[focusedMiastoIndex.value])
    } else if (hasNew && focusedMiastoIndex.value === miastoSuggestions.value.length) {
      selectNewMiasto()
    }
  } else if (e.key === 'Escape') {
    showSuggestions.value = false
    focusedMiastoIndex.value = -1
  }
}

const exactMiastoMatch = computed(() =>
  miastoSuggestions.value.some(n => n.name.toLowerCase() === miastoInput.value.toLowerCase())
)

async function resolveHierarchyNodeId(): Promise<number | null> {
  if (!selectedWojewodztwoId.value) return null
  if (!miastoInput.value.trim()) return selectedWojewodztwoId.value

  if (selectedMiastoId.value) return selectedMiastoId.value

  const res = await api.post<HierarchyNode>('/hierarchy/', {
    name: miastoInput.value.trim(),
    slug: slugify(miastoInput.value.trim()),
    level: 'miasto',
    parent_id: selectedWojewodztwoId.value,
  })
  return res.data.id
}

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  const f = target.files?.[0]
  if (!f) return
  file.value = f
  preview.value = URL.createObjectURL(f)
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  const f = e.dataTransfer?.files[0]
  if (!f) return
  file.value = f
  preview.value = URL.createObjectURL(f)
}

function validate(): boolean {
  const e: Record<string, string> = {}
  if (!file.value) e.file = 'Wybierz plik zdjęcia'
  if (!title.value.trim()) e.title = 'Tytuł jest wymagany'
  if (!description.value.trim()) e.description = 'Opis jest wymagany'
  if (!dateTaken.value.trim()) e.dateTaken = 'Data wykonania jest wymagana'
  if (!selectedWojewodztwoId.value) e.wojewodztwo = 'Województwo jest wymagane'
  if (selectedWojewodztwoId.value && !miastoInput.value.trim()) e.miasto = 'Miasto jest wymagane'
  const tagList = tags.value.split(',').map(t => t.trim()).filter(Boolean)
  if (tagList.length === 0) e.tags = 'Podaj co najmniej jeden tag'
  errors.value = e
  return Object.keys(e).length === 0
}

async function handleSubmit() {
  if (!validate()) return

  errors.value = {}
  loading.value = true

  const nodeId = await resolveHierarchyNodeId()

  const formData = new FormData()
  formData.append('file', file.value!)
  formData.append('title', title.value)
  formData.append('description', description.value)
  formData.append('date_taken', displayToIso(dateTaken.value, datePrecision.value))
  formData.append('date_precision', datePrecision.value)
  if (locationText.value) formData.append('location_text', locationText.value)
  if (nodeId) formData.append('hierarchy_node_id', String(nodeId))
  formData.append('tags', tags.value)

  try {
    const photo = await uploadPhoto(formData)
    router.push({ name: 'photo-detail', params: { id: photo.id } })
  } catch (e: any) {
    errors.value = { submit: e.response?.data?.detail || 'Błąd przesyłania' }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-[var(--color-on-bg)] mb-6">Dodaj zdjęcie</h1>

    <form @submit.prevent="handleSubmit" class="flex flex-col gap-5">
      <div v-if="errors.submit" class="p-3 rounded bg-red-100 text-[var(--color-error)] text-sm" role="alert">
        {{ errors.submit }}
      </div>

      <div
        class="border-2 border-dashed border-[var(--color-border)] rounded-lg p-8 text-center cursor-pointer hover:border-[var(--color-primary)] transition-colors"
        @dragover.prevent @drop="onDrop" @click="($refs.fileInput as HTMLInputElement).click()" role="button"
        tabindex="0" aria-label="Przeciągnij zdjęcie lub kliknij aby wybrać"
        @keydown.enter="($refs.fileInput as HTMLInputElement).click()">
        <img v-if="preview" :src="preview" alt="Podgląd" class="max-h-48 mx-auto mb-3 rounded" />
        <p v-else class="text-[var(--color-muted)]">Przeciągnij zdjęcie lub kliknij aby wybrać</p>
        <p v-if="file" class="text-sm text-[var(--color-on-surface)]">{{ file.name }}</p>
        <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp,image/tiff" class="hidden"
          @change="onFileChange" />
      </div>
      <p v-if="errors.file" class="text-[var(--color-error)] text-xs -mt-3">{{ errors.file }}</p>

      <div>
        <label for="title" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Tytuł *</label>
        <input id="title" v-model="title" type="text"
          :class="['w-full px-3 py-2 rounded-md border bg-[var(--color-bg)] text-[var(--color-on-bg)]', errors.title ? 'border-[var(--color-error)]' : 'border-[var(--color-border)]']" />
        <p v-if="errors.title" class="text-[var(--color-error)] text-xs mt-1">{{ errors.title }}</p>
      </div>

      <div>
        <label for="description" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Opis *</label>
        <textarea id="description" v-model="description" rows="3"
          :class="['w-full px-3 py-2 rounded-md border bg-[var(--color-bg)] text-[var(--color-on-bg)]', errors.description ? 'border-[var(--color-error)]' : 'border-[var(--color-border)]']" />
        <p v-if="errors.description" class="text-[var(--color-error)] text-xs mt-1">{{ errors.description }}</p>
      </div>

      <div class="flex flex-col gap-3">
        <p class="block text-sm font-medium text-[var(--color-on-surface)]">Lokalizacja w hierarchii</p>

        <div>
          <label for="wojewodztwo" class="block text-xs text-[var(--color-muted)] mb-0.5">Województwo *</label>
          <select id="wojewodztwo" :value="selectedWojewodztwoId ?? ''"
            @change="onWojewodztwoChange(($event.target as HTMLSelectElement).value)"
            :class="['w-full px-3 py-2 rounded-md border bg-[var(--color-bg)] text-[var(--color-on-bg)]', errors.wojewodztwo ? 'border-[var(--color-error)]' : 'border-[var(--color-border)]']">
            <option value="">— wybierz województwo —</option>
            <option v-for="node in wojewodztwa" :key="node.id" :value="node.id">{{ node.name }}</option>
          </select>
          <p v-if="errors.wojewodztwo" class="text-[var(--color-error)] text-xs mt-1">{{ errors.wojewodztwo }}</p>
        </div>

        <div v-if="selectedWojewodztwoId" class="relative">
          <label for="miasto" class="block text-xs text-[var(--color-muted)] mb-0.5">Miasto *</label>
          <input id="miasto" v-model="miastoInput" type="text" autocomplete="off"
            placeholder="Wpisz nazwę lub wybierz z listy…" role="combobox" aria-haspopup="listbox"
            :aria-expanded="showSuggestions && (miastoSuggestions.length > 0 || !!miastoInput.trim())"
            aria-controls="miasto-listbox" aria-autocomplete="list"
            :aria-activedescendant="focusedMiastoIndex >= 0 ? `miasto-option-${focusedMiastoIndex}` : undefined"
            :class="['w-full px-3 py-2 rounded-md border bg-[var(--color-bg)] text-[var(--color-on-bg)]', errors.miasto ? 'border-[var(--color-error)]' : 'border-[var(--color-border)]']"
            @input="onMiastoInput" @focus="onMiastoInput" @blur="onMiastoBlur" @keydown="onMiastoKeydown" />
          <ul v-if="showSuggestions && (miastoSuggestions.length > 0 || miastoInput.trim())" id="miasto-listbox"
            class="absolute z-10 w-full mt-1 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] shadow-md max-h-52 overflow-y-auto"
            role="listbox">
            <li v-for="(node, i) in miastoSuggestions" :key="node.id" :id="`miasto-option-${i}`" role="option"
              :aria-selected="i === focusedMiastoIndex"
              :class="['px-3 py-2 cursor-pointer text-[var(--color-on-surface)]', i === focusedMiastoIndex ? 'bg-[var(--color-bg)]' : 'hover:bg-[var(--color-bg)]']"
              @mousedown.prevent="selectMiasto(node)">
              {{ node.name }}
            </li>
            <li v-if="miastoInput.trim() && !exactMiastoMatch" :id="`miasto-option-${miastoSuggestions.length}`"
              role="option" :aria-selected="focusedMiastoIndex === miastoSuggestions.length"
              :class="['px-3 py-2 cursor-pointer italic text-[var(--color-primary)]', focusedMiastoIndex === miastoSuggestions.length ? 'bg-[var(--color-bg)]' : 'hover:bg-[var(--color-bg)]']"
              @mousedown.prevent="selectNewMiasto">
              Dodaj: „{{ miastoInput.trim() }}"
            </li>
          </ul>
          <p v-if="errors.miasto" class="text-[var(--color-error)] text-xs mt-1">{{ errors.miasto }}</p>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label for="dateTaken" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Data
            wykonania *</label>
          <input id="dateTaken" :value="dateTaken" type="text" :placeholder="datePlaceholder"
            :class="['w-full px-3 py-2 rounded-md border bg-[var(--color-bg)] text-[var(--color-on-bg)]', errors.dateTaken ? 'border-[var(--color-error)]' : 'border-[var(--color-border)]']"
            @input="handleDateInput" />
          <p v-if="errors.dateTaken" class="text-[var(--color-error)] text-xs mt-1">{{ errors.dateTaken }}</p>
        </div>
        <div>
          <label for="datePrecision" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Dokładność
            daty</label>
          <select id="datePrecision" v-model="datePrecision"
            class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]">
            <option value="year">Rok</option>
            <option value="month">Miesiąc</option>
            <option value="day">Dzień</option>
          </select>
        </div>
      </div>

      <div>
        <label for="locationText" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Lokalizacja
          (opis tekstowy)</label>
        <input id="locationText" v-model="locationText" type="text" placeholder="np. ul. Floriańska, Kraków"
          class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
      </div>

      <div>
        <label for="tags" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Tagi * (rozdzielone
          przecinkami)</label>
        <input id="tags" v-model="tags" type="text" placeholder="np. architektura, kościół, rynek"
          :class="['w-full px-3 py-2 rounded-md border bg-[var(--color-bg)] text-[var(--color-on-bg)]', errors.tags ? 'border-[var(--color-error)]' : 'border-[var(--color-border)]']" />
        <p v-if="errors.tags" class="text-[var(--color-error)] text-xs mt-1">{{ errors.tags }}</p>
      </div>

      <button type="submit" :disabled="loading"
        class="px-4 py-2 rounded-md bg-[var(--color-primary)] text-[var(--color-on-primary)] font-medium cursor-pointer disabled:opacity-50">
        {{ loading ? 'Przesyłanie...' : 'Dodaj zdjęcie' }}
      </button>
    </form>
  </div>
</template>
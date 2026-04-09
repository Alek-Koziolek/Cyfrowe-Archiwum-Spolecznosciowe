<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { adminUpdatePhoto } from '../../api/admin'
import { updatePhoto } from '../../api/photos'
import api from '../../api/client'
import type { Photo } from '../../types/photo'
import type { HierarchyNode } from '../../types/hierarchy'
import { maskDateInput, isoToDisplay, displayToIso } from '../../utils/date'

const props = defineProps<{ photo: Photo; isAdmin?: boolean }>()
const emit = defineEmits<{
  saved: [photo: Photo]
  close: []
}>()

const dialogRef = ref<HTMLElement>()

function getFocusable(): HTMLElement[] {
  return Array.from(
    dialogRef.value?.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    ) ?? []
  )
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    emit('close')
    return
  }
  if (e.key === 'Tab') {
    const focusable = getFocusable()
    if (focusable.length === 0) return
    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault()
        last.focus()
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }
  }
}

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
})

const title = ref(props.photo.title)
const description = ref(props.photo.description ?? '')
const datePrecision = ref<'year' | 'month' | 'day' | ''>(props.photo.date_precision ?? '')
const dateTaken = ref(isoToDisplay(props.photo.date_taken ?? '', datePrecision.value))
const locationText = ref(props.photo.location_text ?? '')
const tags = ref(props.photo.tags.join(', '))
const error = ref('')
const saving = ref(false)

const datePlaceholder = computed(() => {
  if (datePrecision.value === 'day') return 'DD.MM.RRRR'
  if (datePrecision.value === 'month') return 'MM.RRRR'
  return 'RRRR'
})

watch(datePrecision, () => { dateTaken.value = '' })

function handleDateInput(e: Event) {
  dateTaken.value = maskDateInput((e.target as HTMLInputElement).value, datePrecision.value)
}

const wojewodztwa = ref<HierarchyNode[]>([])
const selectedWojewodztwoId = ref<number | null>(null)
const miastoInput = ref('')
const selectedMiastoId = ref<number | null>(null)
const miastoSuggestions = ref<HierarchyNode[]>([])
const showSuggestions = ref(false)
const focusedMiastoIndex = ref(-1)
let suggestTimer: ReturnType<typeof setTimeout> | null = null

function slugify(name: string): string {
  const map: Record<string, string> = {
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n',
    'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
  }
  return name.toLowerCase().replace(/[ąćęłńóśźż]/g, ch => map[ch] ?? ch).replace(/\s+/g, '-')
}

onMounted(async () => {
  document.addEventListener('keydown', handleKeydown)
  const focusable = getFocusable()
  if (focusable.length > 0) focusable[0].focus()

  const res = await api.get<HierarchyNode[]>('/hierarchy')
  wojewodztwa.value = res.data

  const node = props.photo.hierarchy_node
  if (node) {
    if (node.level === 'miasto' && node.parent_id) {
      selectedWojewodztwoId.value = node.parent_id
      miastoInput.value = node.name
      selectedMiastoId.value = node.id
    } else if (node.level === 'wojewodztwo') {
      selectedWojewodztwoId.value = node.id
    }
  }
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

async function handleSave() {
  if (!title.value.trim()) {
    error.value = 'Tytuł jest wymagany'
    return
  }

  error.value = ''
  saving.value = true

  try {
    const nodeId = await resolveHierarchyNodeId()

    const payload: Record<string, unknown> = {
      title: title.value.trim(),
      description: description.value || null,
      date_taken: dateTaken.value ? displayToIso(dateTaken.value, datePrecision.value) : null,
      date_precision: datePrecision.value || null,
      location_text: locationText.value || null,
      tags: tags.value.split(',').map(t => t.trim()).filter(Boolean),
      hierarchy_node_id: nodeId,
    }

    const updated = props.isAdmin
      ? await adminUpdatePhoto(props.photo.id, payload)
      : await updatePhoto(props.photo.id, payload)
    emit('saved', updated)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Błąd zapisu'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="emit('close')">
    <div ref="dialogRef" role="dialog" aria-modal="true" aria-labelledby="edit-dialog-title"
      class="bg-[var(--color-bg)] rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
      <div class="p-6">
        <h2 id="edit-dialog-title" class="text-xl font-bold text-[var(--color-on-bg)] mb-5">Edytuj zdjęcie</h2>
        <div v-if="error" class="mb-4 p-3 rounded bg-red-100 text-[var(--color-error)] text-sm" role="alert">
          {{ error }}
        </div>
        <form @submit.prevent="handleSave" class="flex flex-col gap-4">
          <div>
            <label for="edit-title" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Tytuł
              *</label>
            <input id="edit-title" v-model="title" type="text" required
              class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
          </div>
          <div>
            <label for="edit-description"
              class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Opis</label>
            <textarea id="edit-description" v-model="description" rows="3"
              class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
          </div>
          <div class="flex flex-col gap-3">
            <p class="block text-sm font-medium text-[var(--color-on-surface)]">Lokalizacja w hierarchii</p>
            <div>
              <label for="edit-wojewodztwo" class="block text-xs text-[var(--color-muted)] mb-0.5">Województwo</label>
              <select id="edit-wojewodztwo" :value="selectedWojewodztwoId ?? ''"
                @change="onWojewodztwoChange(($event.target as HTMLSelectElement).value)"
                class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]">
                <option value="">— wybierz województwo —</option>
                <option v-for="node in wojewodztwa" :key="node.id" :value="node.id">{{ node.name }}</option>
              </select>
            </div>
            <div v-if="selectedWojewodztwoId" class="relative">
              <label for="edit-miasto" class="block text-xs text-[var(--color-muted)] mb-0.5">Miasto / Gmina</label>
              <input id="edit-miasto" v-model="miastoInput" type="text" autocomplete="off"
                placeholder="Wpisz nazwę lub wybierz z listy…" role="combobox" aria-haspopup="listbox"
                :aria-expanded="showSuggestions && (miastoSuggestions.length > 0 || !!miastoInput.trim())"
                aria-controls="edit-miasto-listbox" aria-autocomplete="list"
                :aria-activedescendant="focusedMiastoIndex >= 0 ? `edit-miasto-option-${focusedMiastoIndex}` : undefined"
                class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]"
                @input="onMiastoInput" @focus="onMiastoInput" @blur="onMiastoBlur" @keydown="onMiastoKeydown" />
              <ul v-if="showSuggestions && (miastoSuggestions.length > 0 || miastoInput.trim())"
                id="edit-miasto-listbox"
                class="absolute z-10 w-full mt-1 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] shadow-md max-h-52 overflow-y-auto"
                role="listbox">
                <li v-for="(node, i) in miastoSuggestions" :key="node.id" :id="`edit-miasto-option-${i}`" role="option"
                  :aria-selected="i === focusedMiastoIndex"
                  :class="['px-3 py-2 cursor-pointer text-[var(--color-on-surface)]', i === focusedMiastoIndex ? 'bg-[var(--color-bg)]' : 'hover:bg-[var(--color-bg)]']"
                  @mousedown.prevent="selectMiasto(node)">
                  {{ node.name }}
                </li>
                <li v-if="miastoInput.trim() && !exactMiastoMatch"
                  :id="`edit-miasto-option-${miastoSuggestions.length}`" role="option"
                  :aria-selected="focusedMiastoIndex === miastoSuggestions.length"
                  :class="['px-3 py-2 cursor-pointer italic text-[var(--color-primary)]', focusedMiastoIndex === miastoSuggestions.length ? 'bg-[var(--color-bg)]' : 'hover:bg-[var(--color-bg)]']"
                  @mousedown.prevent="selectNewMiasto">
                  Dodaj: „{{ miastoInput.trim() }}"
                </li>
              </ul>
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label for="edit-dateTaken" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Data
                wykonania</label>
              <input id="edit-dateTaken" :value="dateTaken" type="text" :placeholder="datePlaceholder"
                class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]"
                @input="handleDateInput" />
            </div>
            <div>
              <label for="edit-datePrecision"
                class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Dokładność daty</label>
              <select id="edit-datePrecision" v-model="datePrecision"
                class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]">
                <option value="">— brak —</option>
                <option value="year">Rok</option>
                <option value="month">Miesiąc</option>
                <option value="day">Dzień</option>
              </select>
            </div>
          </div>
          <div>
            <label for="edit-locationText"
              class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Lokalizacja (opis tekstowy)</label>
            <input id="edit-locationText" v-model="locationText" type="text" placeholder="np. ul. Floriańska, Kraków"
              class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
          </div>
          <div>
            <label for="edit-tags" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Tagi
              (rozdzielone przecinkami)</label>
            <input id="edit-tags" v-model="tags" type="text" placeholder="np. architektura, kościół, rynek"
              class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
          </div>

          <div class="flex gap-3 justify-end pt-2">
            <button type="button"
              class="px-4 py-2 rounded-md border border-[var(--color-border)] text-[var(--color-on-surface)] cursor-pointer"
              @click="emit('close')">
              Anuluj
            </button>
            <button type="submit" :disabled="saving"
              class="px-4 py-2 rounded-md bg-[var(--color-primary)] text-[var(--color-on-primary)] font-medium cursor-pointer disabled:opacity-50">
              {{ saving ? 'Zapisywanie...' : 'Zapisz' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

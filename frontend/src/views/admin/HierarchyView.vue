<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../api/client'
import { deleteHierarchyNode } from '../../api/admin'
import type { HierarchyNode, HierarchyNodeWithChildren } from '../../types/hierarchy'
import ConfirmModal from '../../components/common/ConfirmModal.vue'

const roots = ref<HierarchyNode[]>([])
const expanded = ref<Record<number, HierarchyNodeWithChildren>>({})
const loading = ref(true)
const error = ref('')

const confirmState = ref<{ message: string; node: HierarchyNode; parentId: number | null } | null>(null)

onMounted(async () => {
  const res = await api.get<HierarchyNode[]>('/hierarchy')
  roots.value = res.data
  loading.value = false
})

async function toggle(node: HierarchyNode) {
  if (expanded.value[node.id]) {
    delete expanded.value[node.id]
    return
  }
  const res = await api.get<HierarchyNodeWithChildren>(`/hierarchy/${node.id}`)
  if (res.data.children.length > 0) {
    expanded.value[node.id] = res.data
  }
}

function remove(node: HierarchyNode, parentId: number | null) {
  const hasChildren = expanded.value[node.id]?.children.length > 0
  const message = hasChildren
    ? `Usunąć „${node.name}" wraz ze wszystkimi podkategoriami? Zdjęcia nie zostaną usunięte, ale stracą przypisanie do tej lokalizacji.`
    : `Usunąć „${node.name}"? Zdjęcia przypisane do tej lokalizacji stracą to przypisanie.`
  confirmState.value = { message, node, parentId }
}

async function onConfirmRemove() {
  if (!confirmState.value) return
  const { node, parentId } = confirmState.value
  confirmState.value = null
  try {
    await deleteHierarchyNode(node.id)
    delete expanded.value[node.id]
    if (parentId === null) {
      roots.value = roots.value.filter(n => n.id !== node.id)
    } else if (expanded.value[parentId]) {
      expanded.value[parentId].children = expanded.value[parentId].children.filter(n => n.id !== node.id)
    }
  } catch {
    error.value = `Nie udało się usunąć „${node.name}".`
  }
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-[var(--color-on-bg)] mb-6">Zarządzaj hierarchią lokalizacji</h1>
    <p class="text-sm text-[var(--color-muted)] mb-4">
      Usunięcie lokalizacji odłącza od niej wszystkie zdjęcia (zdjęcia nie są kasowane).
      Usunięcie województwa usuwa także wszystkie jego podkategorie.
    </p>
    <div v-if="error" class="mb-4 p-3 rounded bg-red-100 text-[var(--color-error)] text-sm" role="alert">{{ error }}
    </div>
    <ConfirmModal v-if="confirmState" :message="confirmState.message" confirm-label="Usuń" @confirm="onConfirmRemove"
      @cancel="confirmState = null" />
    <div v-if="loading" class="text-[var(--color-muted)]">Ładowanie…</div>
    <ul v-else class="space-y-1">
      <li v-for="root in roots" :key="root.id">
        <div class="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-[var(--color-surface)] group">
          <button class="text-[var(--color-muted)] w-4 text-xs" @click="toggle(root)"
            :aria-label="expanded[root.id] ? 'Zwiń' : 'Rozwiń'">
            {{ expanded[root.id] ? '▾' : '▸' }}
          </button>
          <span class="flex-1 text-[var(--color-on-surface)] font-medium">{{ root.name }}</span>
          <span class="text-xs text-[var(--color-muted)] mr-2">{{ root.level }}</span>
          <button class="text-[var(--color-error)] text-sm cursor-pointer" :aria-label="`Usuń ${root.name}`"
            @click="remove(root, null)">
            Usuń
          </button>
        </div>
        <ul v-if="expanded[root.id]" class="ml-6 mt-1 space-y-1">
          <li v-for="child in expanded[root.id].children" :key="child.id">
            <div class="flex items-center gap-2 px-3 py-2 rounded-md hover:bg-[var(--color-surface)] group">
              <span class="w-4" />
              <span class="flex-1 text-[var(--color-on-surface)]">{{ child.name }}</span>
              <span class="text-xs text-[var(--color-muted)] mr-2">{{ child.level }}</span>
              <button class="text-[var(--color-error)] text-sm cursor-pointer" :aria-label="`Usuń ${child.name}`"
                @click="remove(child, root.id)">
                Usuń
              </button>
            </div>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

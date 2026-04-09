<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getStats } from '../../api/admin'

const stats = ref<{ total_users: number; total_photos: number; blocked_users: number } | null>(null)

onMounted(async () => {
  stats.value = await getStats()
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-[var(--color-on-bg)] mb-6">Panel administracyjny</h1>
    <div v-if="stats" class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
      <div class="p-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]">
        <p class="text-3xl font-bold text-[var(--color-on-bg)]">{{ stats.total_users }}</p>
        <p class="text-sm text-[var(--color-muted)]">Użytkownicy</p>
      </div>
      <div class="p-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]">
        <p class="text-3xl font-bold text-[var(--color-on-bg)]">{{ stats.total_photos }}</p>
        <p class="text-sm text-[var(--color-muted)]">Zdjęcia</p>
      </div>
      <div class="p-6 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)]">
        <p class="text-3xl font-bold text-[var(--color-on-bg)]">{{ stats.blocked_users }}</p>
        <p class="text-sm text-[var(--color-muted)]">Zablokowani</p>
      </div>
    </div>
    <div class="flex gap-4">
      <RouterLink to="/admin/users"
        class="px-4 py-2 rounded-md border border-[var(--color-border)] text-[var(--color-on-surface)] no-underline hover:border-[var(--color-primary)]">
        Zarządzaj użytkownikami
      </RouterLink>
      <RouterLink to="/admin/moderation"
        class="px-4 py-2 rounded-md border border-[var(--color-border)] text-[var(--color-on-surface)] no-underline hover:border-[var(--color-primary)]">
        Moderacja zdjęć
      </RouterLink>
      <RouterLink to="/admin/hierarchy"
        class="px-4 py-2 rounded-md border border-[var(--color-border)] text-[var(--color-on-surface)] no-underline hover:border-[var(--color-primary)]">
        Lokalizacje
      </RouterLink>
    </div>
  </div>
</template>

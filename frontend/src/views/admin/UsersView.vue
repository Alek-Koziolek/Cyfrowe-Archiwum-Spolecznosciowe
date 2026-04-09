<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listUsers, toggleBlockUser } from '../../api/admin'
import type { User } from '../../types/user'

const users = ref<User[]>([])
const loading = ref(true)

onMounted(async () => {
  users.value = await listUsers()
  loading.value = false
})

async function handleToggleBlock(user: User) {
  const updated = await toggleBlockUser(user.id)
  const idx = users.value.findIndex((u) => u.id === user.id)
  if (idx >= 0) users.value[idx] = updated
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-[var(--color-on-bg)] mb-6">Zarządzanie użytkownikami</h1>

    <div v-if="loading" class="text-[var(--color-muted)]" role="status">Ładowanie...</div>
    <table v-else class="w-full text-left">
      <thead>
        <tr class="border-b border-[var(--color-border)]">
          <th scope="col" class="py-2 text-sm font-medium text-[var(--color-muted)]">Nazwa</th>
          <th scope="col" class="py-2 text-sm font-medium text-[var(--color-muted)]">Email</th>
          <th scope="col" class="py-2 text-sm font-medium text-[var(--color-muted)]">Rola</th>
          <th scope="col" class="py-2 text-sm font-medium text-[var(--color-muted)]">Status</th>
          <th scope="col" class="py-2 text-sm font-medium text-[var(--color-muted)]">Akcje</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id" class="border-b border-[var(--color-border)]">
          <td class="py-3 text-[var(--color-on-bg)]">{{ u.display_name }}</td>
          <td class="py-3 text-[var(--color-on-surface)]">{{ u.email }}</td>
          <td class="py-3 text-[var(--color-on-surface)]">{{ u.role }}</td>
          <td class="py-3">
            <span :class="u.is_blocked ? 'text-[var(--color-error)]' : 'text-[var(--color-success)]'">
              {{ u.is_blocked ? 'Zablokowany' : 'Aktywny' }}
            </span>
          </td>
          <td class="py-3">
            <button :class="[
              'px-3 py-1 rounded text-sm cursor-pointer',
              u.is_blocked ? 'bg-[var(--color-success)] text-[var(--color-on-success)]' : 'bg-[var(--color-error)] text-[var(--color-on-error)]'
            ]" :aria-label="u.is_blocked ? `Odblokuj ${u.display_name}` : `Zablokuj ${u.display_name}`"
              @click="handleToggleBlock(u)">
              {{ u.is_blocked ? 'Odblokuj' : 'Zablokuj' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

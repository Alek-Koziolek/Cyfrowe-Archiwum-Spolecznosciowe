<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const { register } = useAuth()
const router = useRouter()

const email = ref('')
const password = ref('')
const displayName = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await register(email.value, password.value, displayName.value)
    router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Błąd rejestracji'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-md mx-auto">
    <h1 class="text-2xl font-bold text-[var(--color-on-bg)] mb-6">Rejestracja</h1>

    <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">
      <div v-if="error" class="p-3 rounded bg-red-100 text-[var(--color-error)] text-sm" role="alert">
        {{ error }}
      </div>

      <div>
        <label for="displayName" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Nazwa
          wyświetlana</label>
        <input id="displayName" v-model="displayName" type="text" required autocomplete="nickname"
          class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
      </div>

      <div>
        <label for="email" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Email</label>
        <input id="email" v-model="email" type="email" required autocomplete="email"
          class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
      </div>

      <div>
        <label for="password" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Hasło</label>
        <input id="password" v-model="password" type="password" required minlength="8" autocomplete="new-password"
          class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
      </div>

      <button type="submit" :disabled="loading"
        class="px-4 py-2 rounded-md bg-[var(--color-primary)] text-[var(--color-on-primary)] font-medium cursor-pointer disabled:opacity-50">
        {{ loading ? 'Rejestracja...' : 'Zarejestruj się' }}
      </button>
    </form>

    <p class="mt-4 text-sm text-[var(--color-on-surface)]">
      Masz już konto?
      <RouterLink to="/login" class="text-[var(--color-primary)]">Zaloguj się</RouterLink>
    </p>
  </div>
</template>

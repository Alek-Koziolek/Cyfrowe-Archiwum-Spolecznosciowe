<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const { login } = useAuth()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Błąd logowania'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-md mx-auto">
    <h1 class="text-2xl font-bold text-[var(--color-on-bg)] mb-6">Logowanie</h1>

    <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">
      <div v-if="error" class="p-3 rounded bg-red-100 text-[var(--color-error)] text-sm" role="alert">
        {{ error }}
      </div>

      <div>
        <label for="email" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Email</label>
        <input id="email" v-model="email" type="email" required autocomplete="email"
          class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
      </div>

      <div>
        <label for="password" class="block text-sm font-medium text-[var(--color-on-surface)] mb-1">Hasło</label>
        <input id="password" v-model="password" type="password" required autocomplete="current-password"
          class="w-full px-3 py-2 rounded-md border border-[var(--color-border)] bg-[var(--color-bg)] text-[var(--color-on-bg)]" />
      </div>

      <button type="submit" :disabled="loading"
        class="px-4 py-2 rounded-md bg-[var(--color-primary)] text-[var(--color-on-primary)] font-medium cursor-pointer disabled:opacity-50">
        {{ loading ? 'Logowanie...' : 'Zaloguj się' }}
      </button>
    </form>

    <p class="mt-4 text-sm text-[var(--color-on-surface)]">
      Nie masz konta?
      <RouterLink to="/register" class="text-[var(--color-primary)]">Zarejestruj się</RouterLink>
    </p>
  </div>
</template>

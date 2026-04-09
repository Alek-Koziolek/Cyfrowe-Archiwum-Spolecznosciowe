<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '../../composables/useAuth'
import ThemeSwitcher from '../common/ThemeSwitcher.vue'

const { isAuthenticated, isAdmin, isContributor, user, logout } = useAuth()
const mobileMenuOpen = ref(false)
const router = useRouter()

function handleLogout() {
  logout()
  router.push('/')
}
</script>

<template>
  <header class="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
    <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Nawigacja">
      <div class="flex items-center justify-between min-h-16 py-3 flex-wrap gap-y-2">
        <RouterLink to="/" class="text-2xl font-bold text-[var(--color-on-bg)] no-underline shrink-0">
          Archiwum
        </RouterLink>
        <div class="hidden md:flex items-center flex-wrap gap-x-4 gap-y-2 text-lg">
          <RouterLink to="/browse"
            class="text-[var(--color-on-surface)] hover:text-[var(--color-primary)] no-underline">
            Przeglądaj
          </RouterLink>
          <RouterLink to="/search"
            class="text-[var(--color-on-surface)] hover:text-[var(--color-primary)] no-underline">
            Szukaj
          </RouterLink>
          <template v-if="isAuthenticated">
            <RouterLink v-if="isContributor" to="/upload"
              class="text-[var(--color-on-surface)] hover:text-[var(--color-primary)] no-underline">
              Dodaj zdjęcie
            </RouterLink>
            <RouterLink v-if="isAdmin" to="/admin"
              class="text-[var(--color-on-surface)] hover:text-[var(--color-primary)] no-underline">
              Panel admina
            </RouterLink>
          </template>
          <ThemeSwitcher />
          <template v-if="isAuthenticated">
            <RouterLink to="/profile"
              class="text-[var(--color-on-surface)] hover:text-[var(--color-primary)] no-underline">
              {{ user?.display_name }}
            </RouterLink>
            <button class="px-4 py-2 rounded-md bg-[var(--color-error)] text-[var(--color-on-error)] cursor-pointer"
              @click="handleLogout">
              Wyloguj
            </button>
          </template>
          <template v-else>
            <RouterLink to="/login"
              class="px-4 py-2 rounded-md bg-[var(--color-primary)] text-[var(--color-on-primary)] no-underline">
              Zaloguj
            </RouterLink>
          </template>
        </div>
        <button class="md:hidden p-3 text-[var(--color-on-surface)] cursor-pointer" :aria-expanded="mobileMenuOpen"
          aria-controls="mobile-menu" aria-label="Menu" @click="mobileMenuOpen = !mobileMenuOpen">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div v-if="mobileMenuOpen" id="mobile-menu" class="md:hidden pb-5 flex flex-col gap-4 text-lg">
        <RouterLink to="/browse" class="text-[var(--color-on-surface)] no-underline py-1"
          @click="mobileMenuOpen = false">
          Przeglądaj</RouterLink>
        <RouterLink to="/search" class="text-[var(--color-on-surface)] no-underline py-1"
          @click="mobileMenuOpen = false">
          Szukaj</RouterLink>
        <template v-if="isAuthenticated">
          <RouterLink v-if="isContributor" to="/upload" class="text-[var(--color-on-surface)] no-underline py-1"
            @click="mobileMenuOpen = false">Dodaj zdjęcie</RouterLink>
          <RouterLink v-if="isAdmin" to="/admin" class="text-[var(--color-on-surface)] no-underline py-1"
            @click="mobileMenuOpen = false">Panel admina</RouterLink>
          <RouterLink to="/profile" class="text-[var(--color-on-surface)] no-underline py-1"
            @click="mobileMenuOpen = false">{{ user?.display_name }}</RouterLink>
          <button class="text-left text-[var(--color-error)] cursor-pointer py-1"
            @click="handleLogout(); mobileMenuOpen = false">Wyloguj</button>
        </template>
        <template v-else>
          <RouterLink to="/login" class="text-[var(--color-primary)] no-underline py-1" @click="mobileMenuOpen = false">
            Zaloguj</RouterLink>
        </template>
        <ThemeSwitcher />
      </div>
    </nav>
  </header>
</template>

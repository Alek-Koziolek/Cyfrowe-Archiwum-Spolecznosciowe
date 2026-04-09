<script setup lang="ts">
import { useTheme } from '../../composables/useTheme'

const { theme, themes, setTheme } = useTheme()
</script>

<template>
  <div class="flex items-center gap-2" role="radiogroup" aria-label="Wybierz motyw">
    <button v-for="t in themes" :key="t.value" role="radio" :aria-checked="theme === t.value" :class="[
      'px-4 py-2 rounded-md font-medium transition-colors',
      'border cursor-pointer',
      theme === t.value
        ? 'border-[var(--color-primary)] bg-[var(--color-primary)] text-[var(--color-on-primary)]'
        : 'border-[var(--color-border)] text-[var(--color-on-surface)] hover:border-[var(--color-primary)]',
    ]" @click="setTheme(t.value)">
      {{ t.label }}
    </button>
  </div>
</template>

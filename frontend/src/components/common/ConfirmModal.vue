<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'

defineProps<{
  message: string
  confirmLabel?: string
  cancelLabel?: string
  danger?: boolean
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
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
    emit('cancel')
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

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  const focusable = getFocusable()
  if (focusable.length > 0) focusable[0].focus()
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="emit('cancel')">
    <div ref="dialogRef" role="dialog" aria-modal="true" aria-labelledby="confirm-dialog-msg"
      class="bg-[var(--color-bg)] rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
      <p id="confirm-dialog-msg" class="text-[var(--color-on-bg)] mb-6">{{ message }}</p>
      <div class="flex gap-3 justify-end">
        <button type="button"
          class="px-4 py-2 rounded-md border border-[var(--color-border)] text-[var(--color-on-surface)] cursor-pointer"
          @click="emit('cancel')">
          {{ cancelLabel ?? 'Anuluj' }}
        </button>
        <button type="button" class="px-4 py-2 rounded-md font-medium cursor-pointer text-[var(--color-on-error)]"
          :class="danger !== false ? 'bg-[var(--color-error)]' : 'bg-[var(--color-primary)] text-[var(--color-on-primary)]'"
          @click="emit('confirm')">
          {{ confirmLabel ?? 'Potwierdź' }}
        </button>
      </div>
    </div>
  </div>
</template>

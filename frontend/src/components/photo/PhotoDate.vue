<script setup lang="ts">
import { computed } from 'vue'
import { formatDate } from '../../utils/date'

const props = defineProps<{
  dateTaken: string | null
  datePrecision: 'year' | 'month' | 'day' | null
}>()

const formatted = computed(() => formatDate(props.dateTaken, props.datePrecision))
</script>

<template>
  <span v-if="formatted">{{ formatted }}</span>
</template>

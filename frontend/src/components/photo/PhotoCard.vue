<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { Photo } from '../../types/photo'
import { thumbnailUrl } from '../../api/photos'
import PhotoDate from './PhotoDate.vue'

defineProps<{ photo: Photo }>()
</script>

<template>
  <RouterLink :to="{ name: 'photo-detail', params: { id: photo.id } }"
    class="block rounded-lg border border-[var(--color-border)] overflow-hidden hover:shadow-lg transition-shadow no-underline group">
    <div class="aspect-[4/3] bg-[var(--color-surface)] overflow-hidden">
      <img :src="thumbnailUrl(photo.id)" :alt="photo.title"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform" loading="lazy" />
    </div>
    <div class="p-4">
      <h3 class="text-base font-semibold text-[var(--color-on-bg)] truncate">
        {{ photo.title }}
      </h3>
      <p v-if="photo.hierarchy_node" class="text-sm text-[var(--color-muted)] truncate mt-1">
        {{ photo.hierarchy_node.parent ? `${photo.hierarchy_node.name}, ${photo.hierarchy_node.parent.name}` :
          photo.hierarchy_node.name }}
      </p>
      <p v-else-if="photo.location_text" class="text-sm text-[var(--color-muted)] truncate mt-1">
        {{ photo.location_text }}
      </p>
      <p v-if="photo.date_taken" class="text-sm text-[var(--color-muted)] mt-1">
        <PhotoDate :date-taken="photo.date_taken" :date-precision="photo.date_precision" />
      </p>
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { ArrowLeft, Repeat } from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  filters: ItemFilters
  isDefault: boolean
}>()

const { open, filters, isDefault } = toRefs(props)

const emit = defineEmits<{
  (event: 'update:open', open: boolean): void
  (event: 'update:filters', filters: ItemFilters): void
  (event: 'close' | 'reset'): void
}>()

function close() {
  emit('update:open', false)
  emit('close')
}
</script>

<template>
  <Drawer
    class="ItemExploreFiltersDrawer"
    :model-value="open"
    @update:model-value="open => emit('update:open', open ?? false)"
  >
    <div class="header">
      <IconButton
        class="Toggle"
        @click="close"
      >
        <ArrowLeft
          :size="32"
          :stroke-width="2"
        />
      </IconButton>
      <h1>Filtres</h1>
      <IconButton
        :disabled="isDefault"
        @click="() => emit('reset')"
      >
        <Repeat
          :size="24"
          :stroke-width="2"
        />
      </IconButton>
    </div>

    <!-- Filters main -->
    <ItemExploreFilters
      class="filters"
      :model-value="filters"
      @update:model-value="filters => emit('update:filters', filters)"
    />
  </Drawer>
</template>

<style scoped lang="scss">
.ItemExploreFiltersDrawer {
  @include flex-column;
  align-items: stretch;
  overflow-y: scroll;

  .header {
    @include flex-row;
    justify-content: space-between;
    gap: 16px;
    padding: 0 1rem;
    height: 64px;
  }

  .filters {
    padding: 1rem;
  }
}
</style>

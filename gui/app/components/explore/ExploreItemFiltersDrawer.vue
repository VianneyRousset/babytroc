<script setup lang="ts">
const open = defineModel<boolean>()
</script>

<template>
  <div>
    <Drawer v-model="open">
      <div>
        <Toggle
          v-model:pressed="open"
          class="Toggle"
        >
          <ArrowLeft
            :size="32"
            :stroke-width="2"
          />
        </Toggle>
        <h1>Filtres</h1>
        <IconButton
          :disabled="true"
        >
          <Repeat
            :size="24"
            :stroke-width="2"
          />
        </IconButton>
      </div>

      <!-- Filters main -->
      <ItemExploreFilters />
    </Drawer>
  </div>
</template>

<style scoped lang="scss">
</style>

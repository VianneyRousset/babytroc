<script setup lang="ts">
const filters = defineModel<ItemFilters>({ required: true })
</script>

<template>
  <div class="ExploreItemFilters">
    <h2>Disponibilité</h2>
    <div class="checkbox-group">
      <Checkbox v-model="filters.available">
        Disponible
      </Checkbox>
      <Checkbox v-model="filters.unavailable">
        Non-disponible
      </Checkbox>
    </div>

    <h2>Age</h2>
    <AgeRangeInput v-model="filters.targetedAge" />

    <h2>Régions</h2>
    <RegionsMap v-model="filters.regions" />
    <RegionsCheckboxes v-model="filters.regions" />
  </div>
</template>

<style scoped lang="scss">
</style>

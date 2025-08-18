<script setup lang="ts">
const stateAvailable = ref(false)
const stateUnavailable = ref(false)
const targetedAge = ref<AgeRange>([1, 2])
const regions = ref(new Set<number>())
</script>

<template>
  <div class="ExploreItemFilters">
    <h2>Disponibilité</h2>
    <div class="checkbox-group">
      <Checkbox v-model="stateAvailable">
        Disponible
      </Checkbox>
      <Checkbox v-model="stateUnavailable">
        Non-disponible
      </Checkbox>
    </div>

    <h2>Age</h2>
    <AgeRangeInput v-model="targetedAge" />

    <h2>Régions</h2>
    <RegionsMap v-model="regions" />
    <RegionsCheckboxes v-model="regions" />
  </div>
</template>

<style scoped lang="scss">
</style>

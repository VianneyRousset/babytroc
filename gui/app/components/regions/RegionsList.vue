<script setup lang="ts">
const model = defineModel<Set<number>>()

function toggle(regionId: number) {
  const _model = unref(model)

  if (_model == null)
    return

  if (_model.has(regionId)) {
    _model.delete(regionId)
  }
  else {
    _model.add(regionId)
  }
}

const { regions } = useRegionsList()
</script>

<template>
  <ul class="RegionsList">
    <li
      v-for="region in regions ?? []"
      :key="`region${region.id}`"
      :active="model?.has(region.id)"
      @click="() => toggle(region.id)"
    >
      {{ region.name }}
    </li>
  </ul>
</template>

<style scoped lang="scss">
.RegionsList {
  @include reset-list;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.6em;
  font-size: round(0.9em, 1px);
  color: $neutral-400;

  li[active="true"] {
    font-weight: 600;
    color: $primary-600;
  }
}
</style>

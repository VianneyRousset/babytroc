<script setup lang="ts" generic="T extends { regions: Array<Region> }">
const props = defineProps<{ item: T }>()

const { item } = toRefs(props)

const { regionIds } = useItemRegions(item)
</script>

<template>
  <RegionsMap
    class="ItemRegionsMap"
    :model-value="regionIds"
  />
</template>

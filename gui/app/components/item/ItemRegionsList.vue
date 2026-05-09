<script setup lang="ts" generic="T extends { region_ids: number[] }">
const props = defineProps<{ item: T }>();

const { item } = toRefs(props);

const { regionIds } = useItemRegions(item);
</script>

<template>
  <RegionsList
    class="ItemRegionsList"
    :model-value="regionIds"
  />
</template>

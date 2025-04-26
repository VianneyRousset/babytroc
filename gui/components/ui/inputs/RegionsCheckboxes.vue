<script setup lang="ts">
const model = defineModel<Set<number>>();

function onChange(regionId: number, state: boolean) {
	if (state) {
		model.value?.add(regionId);
	} else {
		model.value?.delete(regionId);
	}
}

const { data: regions, status } = useApi("/v1/utils/regions", {
	key: "/utils/regions", // provided to avoid missmatch with ssr (bug with openfetch?)
	watch: false,
});
</script>

<template>
  <div>

    <div v-if="status === 'success'" class="checkbox-group">
      <Checkbox v-for="region in regions" :modelValue="model?.has(region.id)"
        @update:modelValue="(v) => v !== undefined && onChange(region.id, v)">{{ region.name }}</Checkbox>
    </div>

  </div>
</template>

<style scoped lang="scss">
svg {

  width: 100%;
  height: auto;

  .region {
    fill: white;
  }

  .region.active {
    fill: $primary-400;
  }

  .wireframe {
    fill: none;
    stroke: $neutral-300;
    stroke-linecap: round;
    stroke-linejoin: round;
    stroke-width: 0.8;
  }
}
</style>

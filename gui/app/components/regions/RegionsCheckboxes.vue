<script setup lang="ts">
const model = defineModel<Set<number>>()

const props = withDefaults(
  defineProps<{
    size?: 'large' | 'normal'
  }>(),
  {
    size: 'normal',
  },
)

const { size } = toRefs(props)

function onChange(regionId: number, state: boolean) {
  if (state) {
    model.value?.add(regionId)
  }
  else {
    model.value?.delete(regionId)
  }
}

const { regions, status } = useRegionsList()
</script>

<template>
  <div>
    <CheckboxGroup v-if="status === 'success'">
      <Checkbox
        v-for="region in regions"
        :key="`region${region.id}`"
        :model-value="model?.has(region.id)"
        :size="size"
        @update:model-value="(v) => v !== undefined && onChange(region.id, v)"
      >
        {{ region.name }}
      </Checkbox>
    </CheckboxGroup>
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

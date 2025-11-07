<script setup lang="ts">
const model = defineModel<Set<number>>()

const props = withDefaults(defineProps<{
  editable?: boolean
  columns?: number
}>(), {
  editable: false,
  columns: 3,
})

const { editable, columns } = toRefs(props)

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
  <ul
    class="RegionsList"
    :class="{ editable }"
  >
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
  align-items: center;
  grid-template-columns: v-bind("`repeat(${columns}, 1fr)`");
  font-size: round(0.9em, 1px);
  color: $neutral-300;

  li {
    padding: 0.6em 0.3em;
  }

  li[active="true"] {
    color: $primary-900;
  }

  &.editable {
    li {
      cursor: pointer;

      &[active="false"]:hover {
        color: $neutral-500;
      }
      &[active="true"]:hover {
        color: $neutral-600;
      }
    }
  }
}
</style>

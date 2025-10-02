<script setup lang="ts" generic="T extends { targeted_age_months: string, regions: Array<Region> }">
const props = defineProps<{ item: T }>()

const { item } = toRefs(props)

const { regions } = useItemRegions(item)
</script>

<template>
  <Minitable class="ItemMinitable">
    <div class="label">
      Âge
    </div>
    <ItemAge :item="item" />
    <div class="label">
      Régions
    </div>
    <ul>
      <li
        v-for="region in regions"
        :key="`region${region.id}`"
      >
        {{ region.name }}
      </li>
    </ul>
  </Minitable>
</template>

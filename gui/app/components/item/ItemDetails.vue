<script setup lang="ts">
const props = defineProps<{ item: Item }>()

const { item } = toRefs(props)

const { formatedTargetedAgeMonths } = useItemTargetedAgeMonths(item)
const { regions, regionsIds } = useItemRegions(item)
</script>

<template>
  <div class="ItemDetails">
    <div class="minitable">
      <div class="label">
        Âge
      </div>
      <div>{{ formatedTargetedAgeMonths }}</div>
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
    </div>
    <RegionsMap :model-value="regionsIds" />
  </div>
</template>

<style lang="scss" scoped>
.minitable {
  display: grid;
  gap: 1em;
  grid-template-columns: 1fr 3fr;
  margin-bottom: 2em;

  .label {
    color: $neutral-400;
  }

  ul {
    @include reset-list;
    @include flex-column;
    gap: 0.5em;
    align-items: flex-start;
  }
}
</style>

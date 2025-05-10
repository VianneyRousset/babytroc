<script setup lang="ts">
const props = defineProps<{ item: Item }>()

const { item } = toRefs(props)

const { formatedTargetedAgeMonths } = useItemTargetedAgeMonths(item)
const { regions, regionsIds } = useItemRegions(item)
</script>

<template>
  <div class="ItemDescriptionAndDetails">
    <PageFold>
      <template #title>
        Description
      </template>
      <div class="name">
        {{ item.name }}
      </div>
      <div>{{ item.description }}</div>
    </PageFold>
    <PageFold>
      <template #title>
        Détails
      </template>
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
    </PageFold>
  </div>
</template>

<style lang="scss" scoped>
.name {
  font-weight: 600;
  margin-bottom: 0.8rem;
  color: $neutral-500;
}
</style>

<script setup lang="ts">
const filters = defineModel<ItemFilters>({ required: true })

const props = withDefaults(
  defineProps<{
    size?: 'large' | 'normal'
  }>(),
  {
    size: 'normal',
  },
)
const { size } = toRefs(props)
</script>

<template>
  <div class="ExploreItemFilters">
    <section>
      <h2>Disponibilité</h2>
      <CheckboxGroup>
        <Checkbox
          v-model="filters.available"
          :size="size"
        >
          Disponible
        </Checkbox>
        <Checkbox
          v-model="filters.unavailable"
          :size="size"
        >
          Non-disponible
        </Checkbox>
      </CheckboxGroup>
    </section>
    <section>
      <h2>Age</h2>
      <AgeRangeInput v-model="filters.targetedAge" />
    </section>
    <section>
      <h2>Régions</h2>
      <RegionsMap v-model="filters.regions" />
      <RegionsCheckboxes
        v-model="filters.regions"
        :size="size"
      />
    </section>
  </div>
</template>

<style scoped lang="scss">
.RegionsMap {
  margin-bottom: 2em;
}
</style>

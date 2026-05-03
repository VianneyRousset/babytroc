<script setup lang="ts">
const props = defineProps<{
  slugs: string[]
}>()

const { categories } = useCategoriesList()

const resolved = computed(() => {
  const all = unref(categories) ?? []
  return props.slugs
    .map(slug => all.find(c => c.slug === slug))
    .filter(c => c != null)
})
</script>

<template>
  <div
    v-if="resolved.length > 0"
    class="ItemCategories"
  >
    <span
      v-for="cat in resolved"
      :key="cat.slug"
      class="tag"
    >
      {{ cat.name }}
    </span>
  </div>
</template>

<style scoped lang="scss">
.ItemCategories {
  display: flex;
  flex-wrap: wrap;
  gap: $space-2;

  .tag {
    background: $bg-tag;
    color: $text-tag;
    padding: $space-1 $space-3;
    border-radius: $radius-pill;
    font-size: 0.8rem;
    font-weight: 500;
  }
}
</style>

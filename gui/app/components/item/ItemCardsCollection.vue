<script setup lang="ts" generic="T extends ItemPreview">
const { items, error, loading } = toRefs(withDefaults(defineProps<{
  items?: Array<T>
  error?: boolean
  loading?: boolean
}>(), {
  error: false,
  loading: false,
}))

const emit = defineEmits<
  (e: 'select', itemId: number) => void
>()
</script>

<template>
  <List
    ref="collection"
    class="ItemCardsCollection"
  >
    <ItemCard
      v-for="item in items ?? []"
      :id="`item${item.id}`"
      :key="`item${item.id}`"
      :item="item"
      @click="() => emit('select', item.id)"
    />
    <ListError v-if="error">
      Une erreur est survenue.
    </ListError>
    <ListLoader v-else-if="loading" />
    <ListEmpty v-else-if="items?.length === 0">
      Aucun résultat
    </ListEmpty>
  </List>
</template>

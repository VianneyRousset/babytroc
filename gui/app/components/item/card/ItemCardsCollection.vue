<script setup lang="ts" generic="T extends ItemPreview">
// items: all the item cards to show
// error: if true, an error message is shown instead of the cards
// loading: if true, show a loading spinner after the cards
const props = withDefaults(defineProps<{
  items?: Array<T>
  error?: boolean
  loading?: boolean
  dense?: boolean
  minColumnsCount?: number
  maxColumnsCount?: number
}>(), {
  error: false,
  loading: false,
  dense: false,
})
const { items, error, loading, dense } = toRefs(props)

// emit a 'select' event with the item id when a card is select
const emit = defineEmits<
  (e: 'select', itemId: number) => void
>()

// adjust the number of columns and the font-size with the width of the component
const { width: collectionElementWidth } = useElementSize(
  useTemplateRef('collection'),
  undefined,
  { box: 'border-box' },
)

const widthSteps = {
  default: [500, 800],
  dense: [200, 500],
}

const columnsCount = computed(() => {
  const _w = unref(collectionElementWidth)
  const _steps = widthSteps[unref(dense) ? 'dense' : 'default']
  const i = _steps.findIndex(step => _w < step)
  return ((i < 0) ? _steps.length : i) + 1
})

const fontSize = computed(() => {
  const _w = unref(collectionElementWidth)
  return _w / unref(columnsCount) / 22
})
</script>

<template>
  <div
    ref="collection"
    class="ItemCardsCollection"
  >
    <ListError v-if="error">
      Une erreur est survenue.
    </ListError>
    <ListEmpty v-else-if="!loading && items?.length === 0">
      Aucun résultat
    </ListEmpty>
    <div class="cards">
      <ItemCard
        v-for="item in items ?? []"
        :id="`item${item.id}`"
        :key="`item${item.id}`"
        :item="item"
        @click="() => emit('select', item.id)"
      />
    </div>
    <ListLoader v-if="!error && loading" />
  </div>
</template>

<style lang="scss" scoped>
.ItemCardsCollection {
  .cards {
    display: grid;
    grid-template-columns: repeat(v-bind('columnsCount'), 1fr);
    gap: 1em;
    padding: 1em;
    font-size: v-bind('fontSize + "px"');
  }
}
</style>

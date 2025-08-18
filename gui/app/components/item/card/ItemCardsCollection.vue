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

const emit = defineEmits<
  (e: 'select', itemId: number) => void
>()

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
  console.log(i, _steps.length)
  if (i < 0) return _steps.length + 1
  return i + 1
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
  </div>
</template>

<style lang="scss" scoped>
.ItemCardsCollection {
  display: grid;
  grid-template-columns: repeat(v-bind('columnsCount'), 1fr);
  gap: 1em;
  padding: 1em;
  font-size: v-bind('fontSize + "px"');

}
</style>

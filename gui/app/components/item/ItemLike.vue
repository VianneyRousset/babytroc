<script setup lang="ts" generic="T extends {id: number, liked?: boolean | null | undefined, likes_count: number}">
import { Heart } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  item: T
  disabled?: boolean
}>(), {
  disabled: false,
})

const { item, disabled } = toRefs(props)

const { like, unlike, error, loading } = useItemLike({ itemId: () => unref(item).id })

// toggle like state
async function onclick() {
  // skip if disabled, undefined like state or loading
  if (unref(disabled) || unref(item).liked == null || unref(loading))
    return

  return unref(item).liked ? await unlike() : await like()
}
</script>

<template>
  <div class="ItemLike">
    <IconButton
      :active="loading"
      @click="onclick"
    >
      <StatsCounter v-model="item.likes_count">
        <Heart
          :class="{ filled: item.liked }"
          :size="32"
          :stroke-width="2"
        />
      </StatsCounter>
    </IconButton>
  </div>
</template>

<style lang="scss" scoped>
.ItemLike {
}
</style>

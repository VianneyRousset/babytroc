<script setup lang="ts">
import { Heart } from 'lucide-vue-next'

import type { AsyncStatus } from '@pinia/colada'

const props = defineProps<{
  item: Item
  itemAsyncStatus: AsyncStatus
  likedItems: Array<Item | ItemPreview>
  likedAsyncStatus: AsyncStatus
}>()

const {
  item,
  itemAsyncStatus,
  likedItems,
  likedAsyncStatus,
} = toRefs(props)

const { isLikedByUser } = useItemLike(item, likedItems)

const { mutateAsync: toggleItemLike, asyncStatus: toggleItemLikeAsyncStatus } = useToggleItemLikeMutation()

// like button is active if like-toggling, item or liked item are loading
const activeLikeButton = computed(() =>
  [toggleItemLikeAsyncStatus, itemAsyncStatus, likedAsyncStatus].some(
    r => unref(r) === 'loading',
  ),
)

// auth
const { loggedIn } = useAuth()
</script>

<template>
  <div class="ItemAvailabilityAndLikesCount">
    <ItemAvailability :available="item.available" />
    <IconButton
      :active="activeLikeButton"
      @click="loggedIn === true ? toggleItemLike({ itemId: item.id, isLikedByUser }) : null"
    >
      <StatsCounter v-model="item.likes_count">
        <Heart
          :class="{ filled: isLikedByUser }"
          :size="32"
          :stroke-width="2"
        />
      </StatsCounter>
    </IconButton>
  </div>
</template>

<style lang="scss" scoped>
.ItemAvailabilityAndLikesCount {
  @include flex-row;
  justify-content: space-between;
  padding: 0 0.5rem;
}
</style>

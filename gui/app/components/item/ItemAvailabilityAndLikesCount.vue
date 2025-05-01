<script setup lang="ts">
import { Heart } from "lucide-vue-next";

import type { AsyncStatus } from "@pinia/colada";

const props = defineProps<{
	item: Item;
	itemAsyncStatus: AsyncStatus;
	likedItems: Array<Item | ItemPreview>;
	likedAsyncStatus: AsyncStatus;
}>();

const {
  item,
  itemAsyncStatus,
  likedItems,
  likedAsyncStatus,
} = toRefs(props);

// current tab
const { currentTab } = useTab();

const { isLikedByUser } = useItemLike(item, likedItems);

const { mutateAsync: toggleItemLike, asyncStatus: toggleItemLikeAsyncStatus } =
	useToggleItemLikeMutation();

// query owner
const { status: ownerStatus, data: owner } = useUserQuery(
	computed(() => toValue(item).owner_id),
);

// like button is active if like-toggling, item or liked item are loading 
const activeLikeButton = computed(() =>
	[toggleItemLikeAsyncStatus, itemAsyncStatus, likedAsyncStatus].some(
		(r) => unref(r) === "loading",
	),
);
</script>

<template>
  <div class="ItemAvailabilityAndLikesCount">
    <Availability :available="item.available" />
    <IconButton @click="toggleItemLike({ itemId: item.id, isLikedByUser })" :active="activeLikeButton">
      <Counter v-model="item.likes_count">
        <Heart :class="{ filled: isLikedByUser }" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      </Counter>
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

<script setup lang="ts">
import type { AsyncStatus } from '@pinia/colada'

const props = defineProps<{
  item: Item
  itemAsyncStatus: AsyncStatus
  me?: UserPrivate | User
  likedItems: Array<Item | ItemPreview>
  likedAsyncStatus: AsyncStatus
  loanRequests: Array<LoanRequest>
}>()

// current tab
const { currentTab } = useTab()

const {
  item,
  itemAsyncStatus,
  me,
  likedItems,
  likedAsyncStatus,
  loanRequests,
} = toRefs(props)

// query owner
const { data: owner } = useUserQuery(
  computed(() => toValue(item).owner_id),
)
</script>

<template>
  <div class="ItemPresentation">
    <!-- Gallery -->
    <ItemImagesGallery :item="item" />

    <!-- Availability and likes count -->
    <ItemAvailabilityAndLikesCount
      :item="item"
      :item-async-status="itemAsyncStatus"
      :liked-items="likedItems"
      :liked-async-status="likedAsyncStatus"
    />

    <!-- Description and details (age and regions) -->
    <ItemDescriptionAndDetails :item="item" />

    <!-- Owner -->
    <NuxtLink
      v-if="owner"
      :to="`/${currentTab}/user/${item.owner_id}`"
      class="reset-link"
    >
      <UserCard :user="owner" />
    </NuxtLink>

    <!-- Request -->
    <ItemRequest
      :item="item"
      :me="me"
      :loan-requests="loanRequests"
    />
  </div>
</template>

<style lang="scss" scoped>
.ItemPresentation {
  @include flex-column;
  align-items: stretch;
  gap: 1rem;

  .status {
    @include flex-row;
    justify-content: space-between;
    padding: 0 0.5rem;
  }

  .name {
    font-weight: 600;
    margin-bottom: 0.8rem;
    color: $neutral-500;
  }
}
</style>

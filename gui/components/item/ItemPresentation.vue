<script setup lang="ts">
import { Heart } from 'lucide-vue-next';

import type { AsyncStatus } from "@pinia/colada";

const props = defineProps<{
  item: Item,
  itemAsyncStatus: AsyncStatus,
  me: User,
  likedItems: Array<Item | ItemPreview>,
  likedAsyncStatus: AsyncStatus,
  loanRequests: Array<LoanRequest>,
}>();

// current tab
const { currentTab } = useTab();

const router = useRouter();

const { item, itemAsyncStatus, me, likedItems, likedAsyncStatus, loanRequests } = toRefs(props);

const { imagesPaths } = useItemImages(item);
const { isLikedByUser } = useItemLike(item, likedItems);
const { formatedTargetedAgeMonths } = useItemTargetedAgeMonths(item);
const { regions, regionsIds } = useItemRegions(item);
const { isOwnedByUser } = useIsItemOwnedByUser(item, me);
const { isRequestedByUser } = useItemLoanRequest(item, loanRequests);

const { mutateAsync: requestItem, asyncStatus: requestItemAsyncStatus } = useRequestItemMutation();
const { mutateAsync: unrequestItem, asyncStatus: unrequestItemAsyncStatus } = useUnrequestItemMutation();
const { mutateAsync: toggleItemLike, asyncStatus: toggleItemLikeAsyncStatus } = useToggleItemLikeMutation();

// query owner
const { status: ownerStatus, data: owner } = useUserQuery(computed(() => toValue(item).owner_id));

const activeLikeButton = computed(() => ([
  toggleItemLikeAsyncStatus,
  itemAsyncStatus,
  likedAsyncStatus,
].some(r => unref(r) === 'loading')
));

async function request(itemId: number) {
  const loanRequest = await requestItem(itemId);
  return navigateTo(router.resolve({
    name: "chats-chat_id",
    params: {
      chat_id: loanRequest.chat_id,
    },
  }));
}

</script>

<template>
  <div class="ItemPresentation">

    <!-- Gallery -->
    <Gallery :images="imagesPaths" />

    <!-- Availability and likes count -->
    <div class="status">
      <Availability :available="item.available" />
      <IconButton @click="toggleItemLike({ itemId: item.id, isLikedByUser })" :active="activeLikeButton">
        <Counter v-model="item.likes_count">
          <Heart :class="{ filled: isLikedByUser }" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
        </Counter>
      </IconButton>

    </div>

    <!-- Description and details (age and regions)-->
    <div>
      <Fold>
        <template v-slot:title>Description</template>
        <div class="name">{{ item.name }}</div>
        <div>{{ item.description }}</div>
      </Fold>
      <Fold>
        <template v-slot:title>Détails</template>
        <div class="minitable">
          <div class="label">Âge</div>
          <div>{{ formatedTargetedAgeMonths }}</div>
          <div class="label">Régions</div>
          <ul>
            <li v-for="region in regions">{{ region.name }}</li>
          </ul>
        </div>
        <RegionsMap :modelValue="regionsIds" />
      </Fold>
    </div>

    <!-- Owner -->
    <NuxtLink v-if="owner" :to="`/${currentTab}/user/${item.owner_id}`" class="reset-link">
      <UserCard :user="owner" />
    </NuxtLink>

    <!-- Request button -->
    <TextButton v-if="!isOwnedByUser && !isRequestedByUser" aspect="bezel" size="large" color="primary"
      :loading="requestItemAsyncStatus === 'loading'" @click="request(item.id)">Demander</TextButton>
    <TextButton v-if="!isOwnedByUser && isRequestedByUser" aspect="outline" size="large" color="neutral"
      :loading="requestItemAsyncStatus === 'loading'" @click="unrequestItem(item.id)">Annuler la demande</TextButton>

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

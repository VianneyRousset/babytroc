import type { AsyncDataRequestStatus } from '#app';

function useItem(item: Ref<Item | null>) {

  const meStore = useMeStore();

  const ownerId: Ref<number | null> = computed(() => item.value?.owner_id ?? null)

  const name: Ref<string | null> = computed(() => item.value?.name ?? null);
  const description: Ref<string | null> = computed(() => item.value?.description ?? null);
  const available: Ref<boolean | null> = computed(() => item.value?.available ?? null);
  const likesCount: Ref<number | null> = computed(() => item.value?.likes_count ?? null);
  const targetedAgeMonths: Ref<[number | null, number | null] | null> = computed(() => item.value?.targeted_age_months ?? null);
  const formatedTargetedAgeMonths: Ref<string | null> = computed(() => targetedAgeMonths.value !== null ? formatTargetedAge(targetedAgeMonths.value[0], targetedAgeMonths.value[1]) : null);

  const images: Ref<Array<string> | null> = computed(() => item.value?.images_names ?? null);
  const regions: Ref<Array<Region> | null> = computed(() => item.value?.regions ?? null);
  const regionsIds: Ref<Set<number>> = computed(() => new Set(item.value?.regions.map((reg) => reg.id) ?? []));

  const isOwnedByUser: Ref<boolean | null> = computed(() => meStore.me?.id === ownerId.value);

  const usersStore = useUsersStore();

  const pendingOwner = ref(false);

  const owner: Ref<User | null> = computedAsync(
    async () => ownerId.value !== null ? (await usersStore.get(ownerId.value)).value : null,
    null,
    {
      lazy: true,
      evaluating: pendingOwner,
    });

  return {
    name,
    description,
    available,
    likesCount,
    targetedAgeMonths,
    formatedTargetedAgeMonths,
    isOwnedByUser,
    ownerId,
    images,
    regions,
    regionsIds,
    owner,
    pendingOwner,
  }
};

function useItemPreview(item: Ref<ItemPreview | null>) {

  const firstImageName = computed(() => item.value?.first_image_name ?? null);
  const firstImagePath = computed(() => item.value !== null ? `/api/v1/images/${firstImageName.value}` : null);
  const targetedAgeMonths: Ref<[number | null, number | null] | null> = computed(() => item.value?.targeted_age_months ?? null);
  const formatedTargetedAgeMonths: Ref<string | null> = computed(() => targetedAgeMonths.value !== null ? formatTargetedAge(targetedAgeMonths.value[0], targetedAgeMonths.value[1]) : null);

  return {
    name: computed(() => item.value?.name ?? null),
    firstImageName,
    firstImagePath,
    targetedAgeMonths,
    formatedTargetedAgeMonths,
  }

}


function useItemLoanRequest(itemId: number) {

  const loanRequestsStore = useLoanRequestsStore();
  const isRequestedByUser: Ref<boolean> = computed(() => unref(loanRequestsStore.hasItem(itemId)));
  const requestStatus: Ref<AsyncDataRequestStatus> = ref("idle");

  async function requestItem() {

    // do not trigger request if already requested
    if (unref(loanRequestsStore.hasItem(itemId)))
      return;

    try {
      requestStatus.value = "pending";

      await loanRequestsStore.requestItem(itemId);

    } catch (error) {
      console.error(error);

      const { $toast } = useNuxtApp();

      $toast.error("Échec de la demande d'emprunt.");
      requestStatus.value = "error";

    } finally {
      await loanRequestsStore.refresh();
      requestStatus.value = "success";
    }
  }

  return {
    isRequestedByUser,
    requestStatus,
    requestItem,
  }

};


function useItemLike(itemId: number, refreshItem: () => Promise<void>) {

  const likedItemsStore = useLikedItemsStore();
  const isLikedByUser = likedItemsStore.has(itemId);
  const likeStatus: Ref<AsyncDataRequestStatus> = ref("idle");

  async function toggleLike() {

    try {

      likeStatus.value = "pending";

      if (isLikedByUser.value) {
        await likedItemsStore.remove(itemId);
      } else {
        await likedItemsStore.add(itemId);
      }

    } catch (error) {
      console.error(error);

      const { $toast } = useNuxtApp();

      $toast.error("Échec de la modification du like.");
      likeStatus.value = "error";

    } finally {
      await refreshItem();
      likeStatus.value = "success";
    }
  }

  return {
    isLikedByUser,
    likeStatus,
    toggleLike,
  }
}


function useItemSave(itemId: number) {

  const savedItemsStore = useSavedItemsStore();
  const isSavedByUser = savedItemsStore.has(itemId);
  const saveStatus: Ref<AsyncDataRequestStatus> = ref("idle");

  async function toggleSave() {

    try {

      saveStatus.value = "pending";

      if (isSavedByUser.value) {
        await savedItemsStore.remove(itemId);
      } else {
        await savedItemsStore.add(itemId);
      }

    } catch (error) {
      console.error(error);

      const { $toast } = useNuxtApp();

      $toast.error("Échec de la modification de la sauvegarde.");
      saveStatus.value = "error";

    } finally {
      saveStatus.value = "success";
    }
  }

  return {
    isSavedByUser,
    saveStatus,
    toggleSave,
  }
}



export {
  useItem,
  useItemPreview,
  useItemLoanRequest,
  useItemLike,
  useItemSave,
};

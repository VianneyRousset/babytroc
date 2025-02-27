import type { ApiResponse } from '#open-fetch'

type User = ApiResponse<"get_user_v1_users__user_id__get">;
type ItemPreview = ApiResponse<'list_items_v1_items_get'>[number];

const useUser = (user: Ref<User | null>) => {

  const name: Ref<string | null> = computed(() => user.value?.name ?? null);
  const avatarSeed: Ref<string | null> = computed(() => user.value?.avatar_seed ?? null);

  const items: Ref<Array<ItemPreview> | null> = computed(() => user.value?.items ?? null);
  const itemsSource = computed(() => useStaticPaginatedSource<ItemPreview>(items.value ?? []));

  const likesCount: Ref<number | null> = computed(() => user.value?.likes_count ?? null);
  const starsCount: Ref<number | null> = computed(() => user.value?.stars_count ?? null);
  const itemsCount: Ref<number | null> = computed(() => items.value?.length ?? null);

  return {
    name,
    avatarSeed,
    items,
    itemsSource,
    likesCount,
    starsCount,
    itemsCount,
  }
};

export { useUser, };

function useUser(user: Ref<User | null>) {

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

function useUserPreview(user: Ref<UserPreview | null>) {

  const name: Ref<string | null> = computed(() => user.value?.name ?? null);
  const avatarSeed: Ref<string | null> = computed(() => user.value?.avatar_seed ?? null);

  return {
    name,
    avatarSeed,
  }

};


export { useUser, useUserPreview };

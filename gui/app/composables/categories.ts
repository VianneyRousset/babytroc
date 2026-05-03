export function useCategoriesList() {
  const { data: categories, ...query } = useApiQuery('/v1/utils/categories', {
    key: ['category', 'categories'],
    refetchOnMount: false,
  })

  return { categories, ...query }
}

type Category = { slug: string, name: string, parent_slug: string | null }

export function useCategoryTree(categories: Ref<Category[] | undefined>) {
  const roots = computed(() =>
    (unref(categories) ?? []).filter(c => c.parent_slug == null),
  )

  function childrenOf(parentSlug: string) {
    return (unref(categories) ?? []).filter(c => c.parent_slug === parentSlug)
  }

  return { roots, childrenOf }
}

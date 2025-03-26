import { ItemQueryAvailability } from '#build/types/open-fetch/schemas/api';



export const useIsLoanRequestActive = (
  item: MaybeRefOrGetter<Item | ItemPreview>,
  likedItems: MaybeRefOrGetter<Array<Item | ItemPreview>>,
) => ({
  isLoan: computed(() => {
    const itemId = toValue(item).id;
    return toValue(likedItems).some(likedItem => likedItem.id === itemId);
  }),
});

export const useItemSave = (
  item: MaybeRefOrGetter<Item | ItemPreview>,
  savedItems: MaybeRefOrGetter<Array<Item | ItemPreview>>,
) => ({
  isSavedByUser: computed(() => {
    const itemId = toValue(item).id;
    return toValue(savedItems).some(savedItem => savedItem.id === itemId);
  }),
});

export const useItemLoanRequest = (
  item: MaybeRefOrGetter<Item | ItemPreview>,
  loanRequests: MaybeRefOrGetter<Array<LoanRequest>>,
) => ({
  isRequestedByUser: computed(() => {
    const itemId = toValue(item).id;
    return toValue(loanRequests).some(req => req.item.id === itemId);
  }),
});

export const useItemFilters = () => {

  const route = useRoute();
  const router = useRouter();

  const searchInput = ref(getQueryParamAsArray(route.query, "q").join(" "));
  const stateAvailable = ref(route.query.av !== ItemQueryAvailability.no);
  const stateUnavailable = ref(route.query.av === ItemQueryAvailability.no || route.query.av === ItemQueryAvailability.all);

  const targetedAge = ref(typeof route.query.mo === "string" ? parseMonthRange(route.query.mo) : [0, null]);
  const regions = reactive(new Set(getQueryParamAsArray(route.query, "reg").map(Number.parseInt)));

  const isFilterActive = computed(() => {

    if (typeof route.query.mo === 'string')
      return true;

    if (typeof route.query.av === 'string' && Object.values(ItemQueryAvailability).includes(route.query.av as ItemQueryAvailability))
      return true;

    if (route.query.reg)
      return true;

    return false;
  });

  const areFilterInputsChanged = computed(() => {

    if (!stateAvailable.value)
      return true;

    if (stateUnavailable.value)
      return true;

    if (targetedAge.value[0] !== 0 || targetedAge.value[1] !== null)
      return true;

    if (regions.size > 0)
      return true;

    return false;
  });

  function filter() {

    const q = unref(searchInput).split(" ").filter((word => word.length > 0));
    const mo = unref(targetedAge);
    const _available = unref(stateAvailable);
    const _unavailable = unref(stateUnavailable);

    const query: ItemQuery = {
      q: q.length > 0 ? q : undefined,
      mo: ((mo[0] ?? 0) > 0 || mo[1] !== null) ? formatMonthRange(mo) : undefined,
      av: _unavailable ? (_available ? ItemQueryAvailability.all : ItemQueryAvailability.no) : undefined,
      reg: regions.size > 0 ? Array.from(regions) : undefined,
    }

    // update page query params
    router.push({ query: query });
  }

  return {
    searchInput,
    stateAvailable,
    stateUnavailable,
    targetedAge,
    regions,
    isFilterActive,
    areFilterInputsChanged,
    filter,
  }
}




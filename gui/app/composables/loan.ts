export const useIsLoanRequestActive = (
  item: MaybeRefOrGetter<Item | ItemPreview>,
  likedItems: MaybeRefOrGetter<Array<Item | ItemPreview>>,
) => ({
  isLoan: computed(() => {
    const itemId = toValue(item).id
    return toValue(likedItems).some(likedItem => likedItem.id === itemId)
  }),
})

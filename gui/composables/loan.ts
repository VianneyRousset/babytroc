import { ItemQueryAvailability } from "#build/types/open-fetch/schemas/api";

export const useIsLoanRequestActive = (
	item: MaybeRefOrGetter<Item | ItemPreview>,
	likedItems: MaybeRefOrGetter<Array<Item | ItemPreview>>,
) => ({
	isLoan: computed(() => {
		const itemId = toValue(item).id;
		return toValue(likedItems).some((likedItem) => likedItem.id === itemId);
	}),
});

export const useItemLoanRequest = (
	item: MaybeRefOrGetter<Item | ItemPreview>,
	loanRequests: MaybeRefOrGetter<Array<LoanRequest>>,
) => ({
	isRequestedByUser: computed(() => {
		const itemId = toValue(item).id;
		return toValue(loanRequests).some((req) => req.item.id === itemId);
	}),
});

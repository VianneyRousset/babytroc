<script setup lang="ts">
import { Heart } from "lucide-vue-next";

import type { AsyncStatus } from "@pinia/colada";

const props = defineProps<{
	item: Item;
	me?: UserPrivate | User;
	loanRequests: Array<LoanRequest>;
}>();

// current tab
const { currentTab } = useTab();

const router = useRouter();

const { loggedIn, loginRoute } = useAuth();

const {
	item,
	me,
	loanRequests,
} = toRefs(props);

const { isOwnedByUser } = useIsItemOwnedByUser(item, me);
const { isRequestedByUser } = useItemLoanRequest(item, loanRequests);

const { mutateAsync: requestItem, asyncStatus: requestItemAsyncStatus } =
	useRequestItemMutation();
const { mutateAsync: unrequestItem, asyncStatus: unrequestItemAsyncStatus } =
	useUnrequestItemMutation();

async function request(itemId: number) {
	const loanRequest = await requestItem(itemId);
	return navigateTo(
		router.resolve({
			name: "chats-chat_id",
			params: {
				chat_id: loanRequest.chat_id,
			},
		}),
	);
}
</script>

<template>
	<div class="ItemRequest">
		<div v-if="loggedIn === true">
	    <TextButton v-if="isOwnedByUser !== true && !isRequestedByUser" aspect="bezel" size="large" color="primary"
	      :loading="requestItemAsyncStatus === 'loading'" @click="request(item.id)">Demander</TextButton>
	    <TextButton v-if="isOwnedByUser !== true && isRequestedByUser" aspect="outline" size="large" color="neutral"
	      :loading="requestItemAsyncStatus === 'loading'" @click="unrequestItem(item.id)">Annuler la demande</TextButton>
		</div>
		<div v-if="loggedIn === false" class="login">
		<div>Connectez vous pour emprunter.</div>
    <TextButton aspect="outline" @click="navigateTo(loginRoute)">Se connecter</TextButton>
		</div>
  </div>
</template>

<style lang="scss" scoped>
.ItemRequest {
  @include flex-column;
  align-items: stretch;

	.login {
	  @include flex-column;
		gap: 0.6rem;
		margin: 1.5rem 0;
	  align-items: center;
	  color: $neutral-800;
		font-style: italic;
		text-align: center;
	}

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

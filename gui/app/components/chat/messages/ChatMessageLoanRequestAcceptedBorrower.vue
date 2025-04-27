<script setup lang="ts">
import { LoanRequestState } from "#build/types/open-fetch/schemas/api";
import { PartyPopper, Import } from "lucide-vue-next";

const props = defineProps<{
	msg: ChatMessage;
	me: User;
	chat: Chat;
	loanRequestId: number;
}>();

// chat
const { me, chat, msg, loanRequestId } = toRefs(props);

// get loan request
const { data: loanRequest } = useBorrowingsLoanRequestQuery(loanRequestId);

// mutations
const {
	mutateAsync: executeLoanRequest,
	asyncStatus: executeLoanRequestAsyncStatus,
} = useExecuteLoanRequestMutation();

// popup
const showPopup = ref(false);

async function execute() {
	await executeLoanRequest({ loanRequestId: unref(loanRequestId) });
	showPopup.value = false;
}
</script>

<template>
  <ChatMessage :me="me" :msg="msg">
    <PartyPopper :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
    <div><b>{{ chat.owner.name }}</b> a accepté de vous prêter de l'objet <b>{{ chat.item.name }}</b></div>
    <template v-if="loanRequest?.state === LoanRequestState.accepted" #buttons>
      <TextButton aspect="outline" color="neutral" @click="showPopup = true">Objet reçu</TextButton>
    </template>

    <Overlay v-model="showPopup">
      <Popup v-model="showPopup">
        <Import :size="128" :strokeWidth="4" :absoluteStrokeWidth="true" />
        <div>Avez-vous bien reçu l'objet <b>{{ chat.item.name }}</b> ? Une fois confirmé, l'emprunt commencera
          officiellement.</div>
        <TextButton aspect="flat" size="large" color="primary" :loading="executeLoanRequestAsyncStatus === 'loading'"
          @click="execute">Objet reçu</TextButton>
      </Popup>
    </Overlay>

  </ChatMessage>
</template>

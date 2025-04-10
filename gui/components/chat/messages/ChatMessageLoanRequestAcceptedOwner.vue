<script setup lang="ts">
import { LoanRequestState } from '#build/types/open-fetch/schemas/api';
import { PartyPopper, CircleOff } from 'lucide-vue-next';

const props = defineProps<{
  msg: ChatMessage,
  me: User,
  chat: Chat,
  loanRequestId: number,
}>();

// chat
const { me, chat, msg, loanRequestId } = toRefs(props);

// get loan request
const { data: loanRequest } = useItemLoanRequestQuery({
  itemId: () => unref(chat).item.id,
  loanRequestId,
});

// muations
const { mutateAsync: rejectLoanRequest, asyncStatus: rejectLoanRequestAsyncStatus } = useRejectLoanRequestMutation();

// popup
const showPopup = ref(false);

</script>

<template>
  <ChatMessage :me="me" :msg="msg">
    <PartyPopper :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
    <div>Vous avez accepté le prêt.</div>
    <template v-if="loanRequest?.state === LoanRequestState.pending" #buttons>
      <TextButton aspect="outline" color="neutral" @click="showPopup = true">Annuler</TextButton>
    </template>

    <Overlay v-model="showPopup">
      <Popup v-model="showPopup">
        <CircleOff :size="128" :strokeWidth="4" :absoluteStrokeWidth="true" />
        <div>Êtes-vous sûr de rejeter la demande d'emprunt de <b>{{ chat.borrower.name }}</b> ?</div>
        <TextButton aspect="flat" size="large" color="red" :loading="rejectLoanRequestAsyncStatus === 'loading'"
          @click="rejectLoanRequest({ itemId: chat.item.id, loanRequestId })">Rejeter</TextButton>
      </Popup>
    </Overlay>

  </ChatMessage>
</template>

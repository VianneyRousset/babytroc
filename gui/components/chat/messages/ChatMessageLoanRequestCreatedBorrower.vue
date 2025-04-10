<script setup lang="ts">
import { LoanRequestState } from '#build/types/open-fetch/schemas/api';
import { MessageCircleQuestion, CircleOff } from 'lucide-vue-next';

const props = defineProps<{
  msg: ChatMessage,
  me: User,
  chat: Chat,
  loanRequestId: number,
}>();

// chat
const { me, chat, msg, loanRequestId } = toRefs(props);

// get loan request
const { data: loanRequest } = useBorrowingsLoanRequestQuery(loanRequestId);

// muations
const { mutateAsync: unrequestItem, asyncStatus: unrequestItemAsyncStatus } = useUnrequestItemMutation();

// popup
const showPopup = ref(false);

</script>

<template>
  <ChatMessage :me="me" :msg="msg">
    <MessageCircleQuestion :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
    <div>Vous avez demandé à emprunter l'objet <b>{{ chat.item.name }}</b></div>
    <template v-if="loanRequest?.state === LoanRequestState.pending" #buttons>
      <TextButton aspect="outline" color="neutral" @click="showPopup = true">Annuler la demande
      </TextButton>
    </template>
    <Overlay v-model="showPopup">
      <Popup v-model="showPopup">
        <CircleOff :size="128" :strokeWidth="4" :absoluteStrokeWidth="true" />
        <div>Êtes-vous sûr de supprimer votre demande d'emprunt ?</div>
        <TextButton aspect="flat" size="large" color="red" :loading="unrequestItemAsyncStatus === 'loading'"
          @click="unrequestItem(chat.item.id)">Supprimer</TextButton>
      </Popup>
    </Overlay>
  </ChatMessage>
</template>

<script setup lang="ts">
import VSwitch from '@lmiller1990/v-switch'
import { LoanRequestState } from '#build/types/open-fetch/schemas/api';
import { MessageCircleQuestion, CircleOff, PartyPopper, Box, CircleStop, Clock, Check } from 'lucide-vue-next';

const props = defineProps<{
  me: User,
  chat: Chat,
  messages: Array<ChatMessage>,
  loanRequests: Array<LoanRequest>,
}>();

const { me, chat, messages, loanRequests } = toRefs(props);

// mutations
const { mutateAsync: unrequestItem } = useUnrequestItemMutation();

function getLoanRequest(loanRequests: MaybeRefOrGetter<Array<LoanRequest>>, id: MaybeRefOrGetter<number>) {
  const _id = toValue(id);
  return toValue(loanRequests).find(req => req.id === _id);
}

function isLoanRequestPending(loanRequestId: MaybeRefOrGetter<number>) {
  const loanRequest = toValue(getLoanRequest(loanRequests, loanRequestId));

  if (!loanRequest)
    return false;

  return loanRequest.state === LoanRequestState.pending;
}

function isLoanRequestAccepted(loanRequestId: MaybeRefOrGetter<number>) {
  const loanRequest = toValue(getLoanRequest(loanRequests, loanRequestId));

  if (!loanRequest)
    return false;

  return loanRequest.state === LoanRequestState.accepted;
}


</script>

<template>
  <ChatMessagesList :me="me" :chat="chat" :messages="messages">

    <template #text="{ msg }">
      <div class="text">
        <div>{{ msg.text }}</div>
      </div>
    </template>

    <template #loan-request-created="{ msg }">
      <div class="text">
        <MessageCircleQuestion :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
        <div>Vous avez demandé à emprunter l'objet <b>{{ chat.item.name }}</b></div>
      </div>
      <div class="buttons" v-if="msg.loan_request_id && isLoanRequestPending(msg.loan_request_id)">
        <TextButton aspect="outline" color="neutral" @click="unrequestItem(msg.item_id)">Annuler la demande
        </TextButton>
      </div>
    </template>

    <template #loan-request-cancelled="{ msg }">
      <div class="text">
        <CircleOff :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
        <div>Demande annulée.</div>
      </div>
      <div class="buttons" v-if="msg.loan_request_id && isLoanRequestAccepted(msg.loan_request_id)">
        <TextButton aspect="outline" color="neutral" @click="">Objet reçu</TextButton>
      </div>
    </template>

    <template #loan-request-accepted="{ msg }">
      <div class="text">
        <PartyPopper :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
        <div>Votre demande a été acceptée par <b>{{ chat.owner.name }}</b></div>
      </div>
    </template>

    <template #loan-request-rejected="{ msg }">
      <div class="text">
        <CircleOff :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
        <div><b>{{ chat.owner.name }}</b> a malheureusement refusé votre demande.</div>
      </div>
    </template>

    <template #loan-started="{ msg }">
      <div class="text">
        <Box :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
        <div>Vous avez reçu l'objet <b>{{ chat.item.name }}</b></div>
      </div>
    </template>

    <template #loan-stopped="{ msg }">
      <div class="text">
        <CircleStop :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
        <div>Vous avez rendu l'objet <b>{{ chat.item.name }}</b></div>
      </div>
    </template>

    <template #item-not-available="{ msg }">
      <div class="text">
        <Clock :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
        <div>L'objet <b>{{ chat.item.name }}</b> n'est plus disponible.</div>
      </div>
    </template>

    <template #item-available="{ msg }">
      <div class="text">
        <Clock :size="24" :strokeWidth="1.33" :absoluteStrokeWidth="true" />
        <div>L'objet <b>{{ chat.item.name }}</b> est à nouveau disponible.</div>
      </div>
    </template>

  </ChatMessagesList>
</template>

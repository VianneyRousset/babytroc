<script setup lang="ts">
import { MessageCircleQuestion, X } from 'lucide-vue-next'
import { LoanRequestState } from '#build/types/open-fetch/schemas/api'

const props = defineProps<{
  message: ChatMessage
  me: User
  chat: Chat
  loanRequestId: number
}>()

const { me, chat, message, loanRequestId } = toRefs(props)

// get loan request
const { data: loanRequest } = useBorrowingsLoanRequestQuery(loanRequestId)

const { unrequest, loading } = useItemLoanRequest({ itemId: unref(chat).item.id })

// popup
const showPopup = ref(false)
</script>

<template>
  <ChatMessage
    :me="me"
    :message="message"
  >
    <MessageCircleQuestion
      :size="24"
      :stroke-width="1.33"
    />
    <div>Vous avez demandé à emprunter l'objet <b>{{ chat.item.name }}</b></div>
    <template
      v-if="loanRequest?.state === LoanRequestState.pending"
      #buttons
    >
      <TextButton
        aspect="outline"
        color="neutral"
        @click="showPopup = true"
      >
        Annuler la demande
      </TextButton>
    </template>
    <Overlay v-model="showPopup">
      <Popup v-model="showPopup">
        <X
          :size="128"
          :stroke-width="1"
        />
        <div>Êtes-vous sûr de supprimer votre demande d'emprunt ?</div>
        <template #actions>
          <TextButton
            aspect="flat"
            size="large"
            color="red"
            :loading="loading"
            @click="unrequest"
          >
            Supprimer
          </TextButton>
          <TextButton
            aspect="outline"
            size="large"
            color="neutral"
            @click="showPopup = false"
          >
            Annuler
          </TextButton>
        </template>
      </Popup>
    </Overlay>
  </ChatMessage>
</template>

<script setup lang="ts">
import { PartyPopper, X } from 'lucide-vue-next'
import { LoanRequestState } from '#build/types/open-fetch/schemas/api'

const props = defineProps<{
  message: ChatMessage
  me: UserPrivate
  chat: Chat
  loanRequestId: number
}>()

// chat
const { me, chat, message, loanRequestId } = toRefs(props)

// get loan request
const { data: loanRequest } = useItemLoanRequestQuery({
  itemId: () => unref(chat).item.id,
  loanRequestId,
})

// muations
const {
  mutateAsync: rejectLoanRequest,
  asyncStatus: rejectLoanRequestAsyncStatus,
} = useRejectLoanRequestMutation()

// popup
const showPopup = ref(false)
</script>

<template>
  <ChatMessage
    :me="me"
    :message="message"
  >
    <PartyPopper
      :size="24"
      :stroke-width="1.33"
    />
    <div>Vous avez accepté le prêt.</div>
    <template
      v-if="loanRequest?.state === LoanRequestState.pending"
      #buttons
    >
      <TextButton
        aspect="outline"
        color="neutral"
        @click="showPopup = true"
      >
        Annuler
      </TextButton>
    </template>

    <Overlay v-model="showPopup">
      <Popup v-model="showPopup">
        <X
          :size="128"
          :stroke-width="1"
        />
        <div>Êtes-vous sûr de rejeter la demande d'emprunt de <b>{{ chat.borrower.name }}</b> ?</div>
        <template #actions>
          <TextButton
            aspect="flat"
            size="large"
            color="red"
            :loading="rejectLoanRequestAsyncStatus === 'loading'"
            @click="rejectLoanRequest({ itemId: chat.item.id, loanRequestId })"
          >
            Rejeter
          </TextButton>
          <TextButton
            aspect="outline"
            size="large"
            color="neutral"
            @click="showPopup = false"
          >
            Ne pas rejeter
          </TextButton>
        </template>
      </Popup>
    </Overlay>
  </ChatMessage>
</template>

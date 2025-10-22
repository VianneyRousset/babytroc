<script setup lang="ts">
import { PartyPopper, Import } from 'lucide-vue-next'
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
const { data: loanRequest } = useBorrowingsLoanRequestQuery(loanRequestId)

// mutations
const {
  mutateAsync: executeLoanRequest,
  asyncStatus: executeLoanRequestAsyncStatus,
} = useExecuteLoanRequestMutation()

// popup
const showPopup = ref(false)

async function execute() {
  await executeLoanRequest({ loanRequestId: unref(loanRequestId) })
  showPopup.value = false
}
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
    <div><b>{{ chat.owner.name }}</b> a accepté de vous prêter de l'objet <b>{{ chat.item.name }}</b></div>
    <template
      v-if="loanRequest?.state === LoanRequestState.accepted"
      #buttons
    >
      <TextButton
        aspect="outline"
        color="neutral"
        @click="showPopup = true"
      >
        Objet reçu
      </TextButton>
    </template>

    <Overlay v-model="showPopup">
      <Popup v-model="showPopup">
        <Import
          :size="128"
          :stroke-width="1"
        />
        <div>
          Avez-vous bien reçu l'objet <b>{{ chat.item.name }}</b> ? Une fois confirmé, l'emprunt commencera
          officiellement.
        </div>
        <template #actions>
          <TextButton
            aspect="flat"
            size="large"
            color="primary"
            :loading="executeLoanRequestAsyncStatus === 'loading'"
            @click="execute"
          >
            Objet reçu
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

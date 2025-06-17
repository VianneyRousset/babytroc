<script setup lang="ts">
import { MessageCircleQuestion, X, Check } from 'lucide-vue-next'
import { LoanRequestState } from '#build/types/open-fetch/schemas/api'

const props = defineProps<{
  msg: ChatMessage
  me: User
  chat: Chat
  loanRequestId: number
}>()

// chat
const { me, chat, msg, loanRequestId } = toRefs(props)

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
const {
  mutateAsync: acceptLoanRequest,
  asyncStatus: acceptLoanRequestAsyncStatus,
} = useAcceptLoanRequestMutation()

// popup
const showAcceptPopup = ref(false)
const showRejectPopup = ref(false)

async function reject() {
  await rejectLoanRequest({
    itemId: unref(chat).item.id,
    loanRequestId: unref(loanRequestId),
  })
  showRejectPopup.value = false
}

async function accept() {
  await acceptLoanRequest({
    itemId: unref(chat).item.id,
    loanRequestId: unref(loanRequestId),
  })
  showAcceptPopup.value = false
}
</script>

<template>
  <ChatMessage
    :me="me"
    :msg="msg"
  >
    <MessageCircleQuestion
      :size="24"
      :stroke-width="1.33"
    />
    <div><b>{{ chat.borrower.name }}</b> voudrait emprunter l'objet <b>{{ chat.item.name }}</b></div>
    <template
      v-if="loanRequest?.state === LoanRequestState.pending"
      #buttons
    >
      <TextButton
        aspect="outline"
        color="neutral"
        @click="showRejectPopup = true"
      >
        Refuser
      </TextButton>
      <TextButton
        aspect="flat"
        color="primary"
        @click="showAcceptPopup = true"
      >
        Accepter
      </TextButton>
    </template>

    <Overlay v-model="showRejectPopup">
      <Popup v-model="showRejectPopup">
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
            @click="reject"
          >
            Rejeter
          </TextButton>
          <TextButton
            aspect="outline"
            size="large"
            color="neutral"
            @click="showRejectPopup = false"
          >
            Annuler
          </TextButton>
        </template>
      </Popup>
    </Overlay>

    <Overlay v-model="showAcceptPopup">
      <Popup v-model="showAcceptPopup">
        <Check
          :size="128"
          :stroke-width="1"
        />
        <div>
          Êtes-vous sûr d'accepter de prêter l'objet <b>{{ chat.item.name }}</b> ?<br>La prochaine étape sera de
          rencontrer <b>{{ chat.borrower.name }}</b> pour lui transporter l'objet.
        </div>
        <template #actions>
          <TextButton
            aspect="flat"
            size="large"
            color="primary"
            :loading="acceptLoanRequestAsyncStatus === 'loading'"
            @click="accept"
          >
            Accepter
          </TextButton>
          <TextButton
            aspect="outline"
            size="large"
            color="neutral"
            @click="showAcceptPopup = false"
          >
            Annuler
          </TextButton>
        </template>
      </Popup>
    </Overlay>
  </ChatMessage>
</template>

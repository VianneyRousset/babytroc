<script setup lang="ts">
import { Import } from 'lucide-vue-next'

const props = defineProps<{
  message: ChatMessage
  me: User
  chat: Chat
  loanId: number
}>()

// chat
const { me, chat, message, loanId } = toRefs(props)

// get loan
const { data: loan } = useLoanQuery({ loanId })

// mutations
const { mutateAsync: endLoan, asyncStatus: endLoanAsyncStatus } = useEndLoanMutation()

// popup
const showPopup = ref(false)

async function end() {
  await endLoan({ loanId: unref(loanId) })
  showPopup.value = false
}
</script>

<template>
  <ChatMessage
    :me="me"
    :message="message"
  >
    <Import
      :size="24"
      :stroke-width="1.33"
    />
    <div>Vous avez prêté l'objet <b>{{ chat.item.name }}</b> à <b>{{ chat.borrower.name }}</b>.</div>
    <template
      v-if="loan?.active"
      #buttons
    >
      <TextButton
        aspect="outline"
        color="neutral"
        @click="showPopup = true"
      >
        Objet rendu
      </TextButton>
    </template>

    <Overlay v-model="showPopup">
      <Popup v-model="showPopup">
        <Import
          :size="128"
          :stroke-width="1"
        />
        <div>
          <b>{{ chat.borrower.name }}</b> a accepté de vous prêter de l'objet <b>{{ chat.item.name }}</b> vous a-t'il
          bien rendu l'objet <b>{{ chat.item.name }}</b> ? Une fois confirmé, l'emprunt sera officiellement terminé.
        </div>
        <template #actions>
          <TextButton
            aspect="flat"
            size="large"
            color="primary"
            :loading="endLoanAsyncStatus === 'loading'"
            @click="end"
          >
            Objet rendu
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

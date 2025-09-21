<script setup lang="ts" generic="T extends { owned?: boolean | null, active_loan_request?: LoanRequest | null, active_loan?: Loan | null }">
import VSwitch from '@lmiller1990/v-switch'
import { ChevronRight } from 'lucide-vue-next'

const props = defineProps<{
  item: T
}>()

const router = useRouter()

const { item } = toRefs(props)

const state = computed<'none' | 'activeBorrowingRequest' | 'activeBorrowing' | 'activeLoan'>(() => {
  const _item = unref(item)

  if (_item.owned === true) {
    if (_item.active_loan)
      return 'activeLoan'
  }
  else {
    if (_item.active_loan != null) {
      return 'activeBorrowing'
    }
    else if (_item.loan_request != null) {
      return 'activeBorrowingRequest'
    }
  }

  return 'none'
})

function navigateToChat() {
  const _item = unref(item)

  if (_item == null)
    throw new Error('Cannot navigate to chat if item is null')

  const chatId = _item.active_loan ?? _item.loan_request

  if (chatId == null)
    throw new Error('Cannot deduce chat id')

  return navigateTo(
    router.resolve({
      name: 'chats-chat_id',
      params: {
        chat_id: chatId,
      },
    }),
  )
}
</script>

<template>
  <div
    v-if="state !== 'none'"
    class="ItemLoanState"
    @click="navigateToChat"
  >
    <div>
      <v-switch :case="state">
        <!-- Active borrowing request -->
        <template #activeBorrowingRequest>
          <div>Demande d'emprunt envoyé</div>
        </template>
        <!-- Active borrowing -->
        <template #activeBorrowing>
          <div>Vous avez emprunté cet objet depuis le xxx</div>
        </template>
        <!-- Active borrowing -->
        <template #activeLoan>
          <div>Prété à xxx depuis le xxx</div>
        </template>
      </v-switch>
    </div>
    <ChevronRight
      :size="32"
      :stroke-width="2"
    />
  </div>
</template>

<style lang="scss" scoped>
.ItemLoanState {
  @include flex-row;
  align-items: stretch;
}
</style>

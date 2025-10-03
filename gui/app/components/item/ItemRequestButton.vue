<script setup lang="ts" generic="T extends {id: number}">
const props = defineProps<{
  item: T
}>()

const { loggedIn, loginRoute } = useAuth()

const { item } = toRefs(props)
const itemId = computed(() => unref(item).id)

const availableForRequest = computed<boolean>(() => {
  const _item = unref(item)
  return _item.available && !_item.owned && !_item.active_loan_request
})

const { request, loading } = useItemLoanRequest({ itemId })

async function requestAndNavigateToChat() {
  const { chatLocation } = await request()
  return navigateTo(chatLocation)
}
</script>

<template>
  <div
    v-if="availableForRequest && loggedIn"
    class="ItemRequestButton request"
  >
    <TextButton
      aspect="bezel"
      size="large"
      color="primary"
      :loading="loading"
      @click="requestAndNavigateToChat"
    >
      Demander
    </TextButton>
  </div>
  <div
    v-else-if="availableForRequest && !loggedIn"
    class="ItemRequestButton login"
  >
    <div>Connectez vous pour emprunter.</div>
    <TextButton
      aspect="outline"
      @click="navigateTo(loginRoute)"
    >
      Se connecter
    </TextButton>
  </div>
</template>

<style lang="scss" scoped>
.ItemRequestButton {
  @include flex-column;
  align-items: stretch;

  &.login {
    @include flex-column;
    gap: 0.6rem;
    margin: 1.5rem 0;
    align-items: center;
    color: $neutral-800;
    font-style: italic;
    text-align: center;
  }
}
</style>

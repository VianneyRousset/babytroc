<script setup lang="ts">
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

const props = withDefaults(defineProps<{
  status?: AsyncStatus
  msgError?: string
  msgSuccess?: string
  msgPlacement?: MsgPlacement
}>(), {
  status: 'idle',
  msgPlacement: 'auto',
})

const message = computed<string | undefined>(() => {
  switch (props.status) {
    case 'idle':
    case 'pending':
      return undefined
    case 'error':
      return props.msgError
    case 'success':
      return props.msgSuccess
  }

  return undefined
})
</script>

<template>
  <VDropdown
    :distance="8"
    :triggers="[]"
    :shown="message != null"
    :auto-hide="false"
    :placement="msgPlacement"
    :theme="`dropdown-${status}`"
  >
    <slot />
    <template #popper>
      {{ message }}
    </template>
  </VDropdown>
</template>

<style scoped lang="scss">
.DropdownMessage {}
</style>

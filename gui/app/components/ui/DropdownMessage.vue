<script setup lang="ts">
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

const props = withDefaults(defineProps<{
  status?: AsyncStatus
  distance?: number
  msgError?: string
  msgSuccess?: string
  msgPlacement?: MsgPlacement
}>(), {
  status: 'idle',
  distance: 8,
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
    :distance="distance"
    :triggers="[]"
    :shown="message != null"
    :auto-hide="false"
    :placement="msgPlacement"
    :theme="`dropdown-${status}`"
    class="DropdownMessage"
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

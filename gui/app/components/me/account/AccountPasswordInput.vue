<script setup lang="ts">
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

const password = defineModel<string>({ required: true })

const emit = defineEmits<{
  (event: 'update:status', valid: AsyncStatus): void
  (event: 'enter'): void
}>()

const touched = ref(false)
const { status, error } = useUserPasswordValidity(password, useThrottle(touched, 1000).value)

watch(status, (_status) => {
  emit('update:status', unref(status))
}, { immediate: true })

watchEffect(() => {
  if (unref(password).length > 0)
    touched.value = true
})
</script>

<template>
  <div class="AccountPasswordInput vbox">
    <TextInput
      v-model="password"
      type="password"
      placeholder="Mot de passe"
      msg-placement="top"
      autofocus
      :tabindex="1"
      :status="status"
      :msg-error="error"
      @blur="touched = true"
      @keyup.enter="emit('enter')"
    />
  </div>
</template>

<style scoped lang="scss">
.AccountPasswordInput {
  @include flex-column;
  align-items: stretch;
  gap: 1rem;
}
</style>

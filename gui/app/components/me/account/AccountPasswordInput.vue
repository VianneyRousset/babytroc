<script setup lang="ts">
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

const props = withDefaults(defineProps<{
  msgPlacement?: MsgPlacement
}>(), {
  msgPlacement: 'auto',
})

const { msgPlacement } = toRefs(props)

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
    <DropdownMessage
      :status="status"
      :msg-error="error"
      :msg-placement="msgPlacement"
    >
      <TextInput
        v-model="password"
        type="password"
        placeholder="Mot de passe"
        autofocus
        :tabindex="1"
        :status="status"
        @blur="touched = true"
        @keyup.enter="emit('enter')"
      />
    </DropdownMessage>
  </div>
</template>

<style scoped lang="scss">
.AccountPasswordInput {
  @include flex-column;
  align-items: stretch;
  gap: 1rem;
}
</style>

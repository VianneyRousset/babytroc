<script setup lang="ts">
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

const props = withDefaults(defineProps<{
  modelValue: string
  msgPlacement?: MsgPlacement
}>(), {
  msgPlacement: 'auto',
})
const { msgPlacement } = toRefs(props)

const emit = defineEmits<{
  (event: 'update:modelValue', modelValue: string): void
  (event: 'update:status', valid: AsyncStatus): void
  (event: 'enter'): void
}>()

const email = ref<string>(unref(props.modelValue))

const touched = ref(false)
const { email: cleanedEmail, status, error } = useUserEmailValidity(email, useThrottle(touched, 1000).value)

watch(() => props.modelValue, (_model) => {
  email.value = _model
})
watch(status, (_status) => {
  emit('update:status', unref(status))
}, { immediate: true })

watch(cleanedEmail, _email => emit('update:modelValue', _email))

watchEffect(() => {
  if (unref(email).length > 0)
    touched.value = true
})
</script>

<template>
  <div class="AccountEmail vbox">
    <WithDropdownMessage
      :status="status"
      :msg-error="error"
      :msg-placement="msgPlacement"
    >
      <TextInput
        v-model="email"
        type="text"
        placeholder="Email"
        autofocus
        :tabindex="1"
        :status="status"
        @blur="touched = true"
        @keyup.enter="emit('enter')"
      />
    </WithDropdownMessage>
  </div>
</template>

<style scoped lang="scss">
.AccountEmail {
  @include flex-column;
  align-items: stretch;
  gap: 1rem;
}
</style>

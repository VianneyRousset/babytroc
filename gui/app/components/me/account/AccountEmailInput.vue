<script setup lang="ts">
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

const props = defineProps<{
  modelValue: string
}>()
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
  <div class="MeAccountEmail vbox">
    <TextInput
      v-model="email"
      type="text"
      placeholder="Email"
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
.MeAccountEmail {
  @include flex-column;
  align-items: stretch;
  gap: 1rem;
}
</style>

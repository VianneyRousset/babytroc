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

const name = ref<string>(unref(props.modelValue))

const touched = ref(false)
const { name: cleanedName, status, error } = useUserNameValidity(name, useThrottle(touched, 1000).value)

watch(() => props.modelValue, (_model) => {
  name.value = _model
})
watch(status, (_status) => {
  emit('update:status', unref(status))
}, { immediate: true })

watch(cleanedName, _name => emit('update:modelValue', _name))

watchEffect(() => {
  if (unref(name).length > 0)
    touched.value = true
})
</script>

<template>
  <div class="AccountName vbox">
    <DropdownMessage
      :status="status"
      :msg-error="error"
      :msg-placement="msgPlacement"
    >
      <TextInput
        v-model="name"
        type="text"
        placeholder="Pseudonyme"
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
.AccountName {
  @include flex-column;
  align-items: stretch;
  gap: 1rem;
}
</style>

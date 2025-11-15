<script setup lang="ts">
import type { TextInputProps } from '../../ui/inputs/TextInput.vue'

const props = withDefaults(defineProps<{
  msgPlacement?: MsgPlacement
} & Omit<TextInputProps, 'modelValue' | 'status'>>(), {
  type: 'email',
  placeholder: 'Email',
})

const { msgPlacement } = toRefs(props)

const email = defineModel<string>('email', { default: '' })
const valid = defineModel<boolean>('valid')
const emit = defineEmits(['next', 'blur'])

const { status, error, touched } = useAccountEmailValidity(email)

const stop = watchEffect(() => {
  valid.value = unref(status) === 'success'
})

function next() {
  if (unref(valid))
    emit('next')
}

tryOnUnmounted(stop)
</script>

<template>
  <div class="AccountEmailInput">
    <WithDropdownMessage
      :status="status"
      :msg-error="error"
      :msg-placement="msgPlacement"
    >
      <TextInput
        v-model="email"
        v-bind="props"
        :status="status"
        @keyup.enter="next"
        @blur="() => (touched = true)"
      />
    </WithDropdownMessage>
  </div>
</template>

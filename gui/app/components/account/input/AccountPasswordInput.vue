<script setup lang="ts">
import type { TextInputProps } from '../../ui/inputs/TextInput.vue'

const props = withDefaults(defineProps<{
  msgPlacement?: MsgPlacement
} & Omit<TextInputProps, 'modelValue' | 'status'>>(), {
  type: 'password',
  placeholder: 'Mot de passe',
})

const { msgPlacement } = toRefs(props)

const password = defineModel<string>('password', { default: '' })
const valid = defineModel<boolean>('valid')
const emit = defineEmits(['next', 'blur'])

const { status, error, touched } = useAccountPasswordValidity(password)

const stop = watchEffect(() => {
  password.value = avoidConsecutiveWhitespaces(unref(password).trim())
  valid.value = unref(status) === 'success'
})

function next() {
  if (unref(valid))
    emit('next')
}

tryOnUnmounted(stop)
</script>

<template>
  <div class="AccountPasswordInput">
    <WithDropdownMessage
      :status="status"
      :msg-error="error"
      :msg-placement="msgPlacement"
    >
      <TextInput
        v-model="password"
        v-bind="props"
        :status="status"
        @keyup.enter="next"
        @blur="() => (touched = true)"
      />
    </WithDropdownMessage>
  </div>
</template>

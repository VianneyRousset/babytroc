<script setup lang="ts">
const props = defineProps<{
  tabindex?: number
  autofocus?: boolean
  msgPlacement?: MsgPlacement
}>()

const { tabindex, autofocus } = toRefs(props)

const password = defineModel<string>('password', { default: '' })
const valid = defineModel<boolean>('valid')
const emit = defineEmits(['next', 'blur'])

const { status, error, touched } = useAccountPasswordValidity(password)

const stop = watchEffect(() => {
  password.value = avoidConsecutiveWhitespaces(unref(password).trim())
  valid.value = unref(status) === 'success'
})

function next() {
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
        type="password"
        placeholder="Mot de passe"
        :autofocus="autofocus"
        :tabindex="tabindex"
        :status="status"
        @keyup.enter="next"
        @blur="() => (touched = true)"
      />
    </WithDropdownMessage>
  </div>
</template>

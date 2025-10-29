<script setup lang="ts">
const props = defineProps<{
  tabindex?: number
  autofocus?: boolean
  msgPlacement?: MsgPlacement
}>()

const { tabindex, autofocus } = toRefs(props)

const email = defineModel<string>('email', { default: '' })
const valid = defineModel<boolean>('valid')
const emit = defineEmits(['next', 'blur'])

const { status, error, touched } = useAccountEmailValidity(email)

const stop = watchEffect(() => {
  email.value = avoidConsecutiveWhitespaces(unref(email).trim())
  valid.value = unref(status) === 'success'
})

function next() {
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
        type="email"
        placeholder="Email"
        :autofocus="autofocus"
        :tabindex="tabindex"
        :status="status"
        @keyup.enter="next"
        @blur="() => (touched = true)"
      />
    </WithDropdownMessage>
  </div>
</template>

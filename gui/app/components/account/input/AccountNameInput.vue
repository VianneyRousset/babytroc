<script setup lang="ts">
const props = defineProps<{
  tabindex?: number
  autofocus?: boolean
  msgPlacement?: MsgPlacement
}>()

const { tabindex, autofocus } = toRefs(props)

const name = defineModel<string>('name', { default: '' })
const valid = defineModel<boolean>('valid')
const emit = defineEmits(['next', 'blur'])

const { status, error, touched } = useAccountNameValidity(name)

const stop = watchEffect(() => {
  name.value = avoidConsecutiveWhitespaces(unref(name).trim())
  valid.value = unref(status) === 'success'
})

function next() {
  emit('next')
}

tryOnUnmounted(stop)
</script>

<template>
  <div class="AccountNameInput">
    <WithDropdownMessage
      :status="status"
      :msg-error="error"
      :msg-placement="msgPlacement"
    >
      <TextInput
        v-model="name"
        type="text"
        placeholder="Pseudonyme"
        :autofocus="autofocus"
        :tabindex="tabindex"
        :status="status"
        @keyup.enter="next"
        @blur="() => (touched = true)"
      />
    </WithDropdownMessage>
  </div>
</template>

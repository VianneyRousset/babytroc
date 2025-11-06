<script setup lang="ts">
import type { TextInputProps } from '../../ui/inputs/TextInput.vue'

const props = withDefaults(defineProps<{
  msgPlacement?: MsgPlacement
} & Omit<TextInputProps, 'modelValue' | 'status'>>(), {
  type: 'text',
  placeholder: 'Nom',
})

const { msgPlacement } = toRefs(props)

const name = defineModel<string>('name', { default: '' })
const valid = defineModel<boolean>('valid')
const emit = defineEmits(['next', 'blur'])

const { status, error, touched } = useItemNameValidity(name)

const stop = watchEffect(() => {
  name.value = avoidConsecutiveWhitespaces(unref(name).trim())
  valid.value = unref(status) === 'success'
})

function next() {
  if (unref(valid))
    emit('next')
}

tryOnUnmounted(stop)
</script>

<template>
  <div class="ItemNameInput">
    <WithDropdownMessage
      :status="status"
      :msg-error="error"
      :msg-placement="msgPlacement"
    >
      <TextInput
        v-model="name"
        v-bind="props"
        :status="status"
        @keyup.enter="next"
        @blur="() => (touched = true)"
      />
    </WithDropdownMessage>
  </div>
</template>

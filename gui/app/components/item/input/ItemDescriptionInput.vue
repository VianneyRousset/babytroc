<script setup lang="ts">
import type { LongTextInputProps } from '../../ui/inputs/LongTextInput.vue'

const props = withDefaults(defineProps<{
  msgPlacement?: MsgPlacement
} & Omit<LongTextInputProps, 'modelValue' | 'status'>>(), {
  type: 'text',
  placeholder: 'Description',
})

const { msgPlacement } = toRefs(props)

const description = defineModel<string>('description', { default: '' })
const valid = defineModel<boolean>('valid', { default: false })
const touched = defineModel<boolean>('touched', { default: false })

const emit = defineEmits(['next', 'blur'])

const { status, error } = useItemDescriptionValidity(description, touched)

const stop = watchEffect(() => {
  description.value = avoidConsecutiveWhitespaces(unref(description).trim())
  valid.value = unref(status) === 'success'
})

function next() {
  if (unref(valid))
    emit('next')
}

tryOnUnmounted(stop)
</script>

<template>
  <div class="ItemDescriptionInput">
    <WithDropdownMessage
      :status="status"
      :msg-error="error"
      :msg-placement="msgPlacement"
    >
      <LongTextInput
        v-model="description"
        v-bind="props"
        :status="status"
        @keyup.enter="next"
        @blur="() => (touched = true)"
      />
    </WithDropdownMessage>
  </div>
</template>

<script setup lang="ts">
import { Check, TriangleAlert } from 'lucide-vue-next'
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

const model = defineModel<string>()
const emit = defineEmits(['blur'])

const props = withDefaults(defineProps<{
  placeholder?: string
  type?: 'button' | 'checkbox' | 'color' | 'date' | 'datetime-local' | 'email' | 'file' | 'hidden' | 'image' | 'month' | 'number' | 'password' | 'radio' | 'range' | 'reset' | 'search' | 'submit' | 'tel' | 'text' | 'time' | 'url' | 'week'
  autofocus?: boolean
  tabindex?: number
  status?: AsyncStatus
  msgError?: string
  msgSuccess?: string
  msgPlacement?:
    'auto'
    | 'auto-start'
    | 'auto-end'
    | 'top'
    | 'top-start'
    | 'top-end'
    | 'right'
    | 'right-start'
    | 'right-end'
    | 'bottom'
    | 'bottom-start'
    | 'bottom-end'
    | 'left'
    | 'left-start'
    | 'left-end' }>(), {
  status: 'idle',
  msgPlacement: 'auto',
})

const message = computed<string | undefined>(() => {
  switch (props.status) {
    case 'idle':
    case 'pending':
      return undefined
    case 'error':
      return props.msgError
    case 'success':
      return props.msgSuccess
  }

  return undefined
})
</script>

<template>
  <VDropdown
    :distance="8"
    :triggers="[]"
    :shown="message != null"
    :auto-hide="false"
    :placement="msgPlacement"
    :theme="`dropdown-${status}`"
    class="TextInput"
  >
    <input
      v-model="model"
      :placeholder="placeholder"
      :type="type"
      :tabindex="tabindex"
      :autofocus="autofocus"
      @blur="emit('blur')"
    >

    <transition
      name="pop"
      mode="out-in"
      appear
    >
      <LoadingAnimation
        v-if="status === 'pending'"
        :small="true"
        class="icon"
      />
      <TriangleAlert
        v-else-if="status === 'error'"
        class="icon error"
        :size="28"
        :stroke-width="1.5"
      />
      <Check
        v-else-if="status === 'success'"
        class="icon success"
        :size="28"
        :stroke-width="1.5"
      />
    </transition>

    <template #popper>
      {{ message }}
    </template>
  </VDropdown>
</template>

<style scoped lang="scss">
.TextInput {
  @include flex-row;
  position: relative;

  input {
    flex: 1;
    font-size: 1.5rem;
    padding: 0.3rem 0.8rem;
    border-radius: 0.4rem;
  }

  .icon {
    position: absolute;
    right: 6px;

    &.error {
      color: $red-800;
    }
    &.success {
      color: $primary-600;
    }
  }
}
</style>

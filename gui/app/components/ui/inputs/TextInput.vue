<script setup lang="ts">
import { Check, TriangleAlert } from 'lucide-vue-next'

const model = defineModel<string>()

const props = withDefaults(defineProps<{
  placeholder?: string
  type?: 'button' | 'checkbox' | 'color' | 'date' | 'datetime-local' | 'email' | 'file' | 'hidden' | 'image' | 'month' | 'number' | 'password' | 'radio' | 'range' | 'reset' | 'search' | 'submit' | 'tel' | 'text' | 'time' | 'url' | 'week'
  autofocus?: boolean
  tabindex?: number
  loading?: boolean
  error?: string | boolean
  success?: string | boolean
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
  loading: false,
  error: false,
  success: false,
  msgPlacement: 'auto',
})

const { placeholder, type, autofocus, tabindex, msgPlacement } = toRefs(props)

const mode = computed<'loading' | 'error' | 'success' | undefined>(() => {
  if (props.loading) return 'loading'
  if (props.error) return 'error'
  if (props.success) return 'success'
  return undefined
})
const message = computed<string | undefined>(() => {
  const _mode = unref(mode)
  if (_mode === 'error' && typeof props.error === 'string') return props.error
  if (_mode === 'success' && typeof props.success === 'string') return props.success
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
    :theme="`dropdown-${mode}`"
    class="TextInput"
  >
    <input
      v-model="model"
      :placeholder="placeholder"
      :type="type"
      :tabindex="tabindex"
      :autofocus="autofocus"
    >

    <transition
      name="pop"
      mode="out-in"
      appear
    >
      <LoadingAnimation
        v-if="mode === 'loading'"
        :small="true"
        class="icon"
      />
      <TriangleAlert
        v-else-if="mode === 'error'"
        class="icon error"
        :size="28"
        :stroke-width="1.5"
      />
      <Check
        v-else-if="mode === 'success'"
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

<script setup lang="ts">
import { TriangleAlert } from 'lucide-vue-next'

const model = defineModel<string>()

const props = withDefaults(defineProps<{
  placeholder?: string
  type?: 'button' | 'checkbox' | 'color' | 'date' | 'datetime-local' | 'email' | 'file' | 'hidden' | 'image' | 'month' | 'number' | 'password' | 'radio' | 'range' | 'reset' | 'search' | 'submit' | 'tel' | 'text' | 'time' | 'url' | 'week'
  autofocus?: boolean
  tabindex?: number
  error?: string | null
  errorPlacement?:
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
  errorPlacement: 'auto',
})

const { placeholder, type, autofocus, tabindex, error, errorPlacement } = toRefs(props)
</script>

<template>
  <VDropdown
    :distance="8"
    :triggers="[]"
    :shown="error != null"
    :auto-hide="false"
    :placement="errorPlacement"
    theme="dropdown-error"
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
      mode="in-out"
      appear
    >
      <TriangleAlert
        v-if="error != null"
        class="icon"
        :size="28"
        :stroke-width="1.5"
      />
    </transition>

    <template #popper>
      {{ error }}
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
    color: $red-800;
  }
}
</style>

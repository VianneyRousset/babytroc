<script setup lang="ts">
import { Check, TriangleAlert, Eye, EyeOff } from 'lucide-vue-next'
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

const model = defineModel<string>()
const emit = defineEmits(['blur'])

type InputType = ('button' | 'checkbox' | 'color' | 'date' | 'datetime-local' | 'email'
  | 'file' | 'hidden' | 'image' | 'month' | 'number' | 'password' | 'radio' | 'range'
  | 'reset' | 'search' | 'submit' | 'tel' | 'text' | 'time' | 'url' | 'week')

const props = withDefaults(defineProps<{
  placeholder?: string
  type?: InputType
  autofocus?: boolean
  tabindex?: number
  status?: AsyncStatus
}>(), {
  status: 'idle',
})

const inputElement = useTemplateRef<HTMLElement>('input')

watch(inputElement, _el => _el && props.autofocus ? _el.focus() : undefined)

const showPassword = ref<boolean>(false)

const type = computed(() => {
  if (props.type === 'password')
    return unref(showPassword) ? 'text' : 'password'
  return props.type
})
</script>

<template>
  <div class="TextInput">
    <input
      ref="input"
      v-model="model"
      :size="1"
      :placeholder="props.placeholder"
      :type="type"
      :tabindex="props.tabindex"
      :autofocus="props.autofocus"
      @blur="emit('blur')"
    >
    <div class="icons-wrapper">
      <transition
        name="pop"
        mode="out-in"
        appear
      >
        <LoadingAnimation
          v-if="status === 'pending'"
          :small="true"
        />
        <TriangleAlert
          v-else-if="status === 'error'"
          class="error"
          :size="28"
          :stroke-width="1.5"
        />
        <Check
          v-else-if="status === 'success'"
          class="success"
          :size="28"
          :stroke-width="1.5"
        />
      </transition>
      <transition
        name="pop"
        mode="out-in"
      >
        <Eye
          v-if="props.type === 'password' && !showPassword"
          class="visibility"
          :size="28"
          :stroke-width="1.5"
          @click="showPassword = true"
        />
        <EyeOff
          v-else-if="props.type === 'password'"
          class="visibility"
          :size="28"
          :stroke-width="1.5"
          @click="showPassword = false"
        />
      </transition>
    </div>
  </div>
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

  .icons-wrapper {
    @include flex-row;
    gap: 0.3rem;
    position: absolute;
    right: 6px;
    color: $neutral-600;

    .LoadingAnimation {
      width: 28px;
    }

    .visibility {
      cursor: pointer;
    }

    .error {
      color: $red-800;
    }
    .success {
      color: $primary-600;
    }
  }
}
</style>

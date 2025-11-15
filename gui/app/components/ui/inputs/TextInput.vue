<script setup lang="ts">
import { Check, TriangleAlert, Eye, EyeOff } from 'lucide-vue-next'

type InputType = ('email' | 'password' | 'search' | 'tel' | 'text' | 'url')

export type TextInputProps = {
  placeholder?: string
  type?: InputType
  autofocus?: boolean
  tabindex?: number
  status?: 'idle' | 'pending' | 'success' | 'error'
  disabled?: boolean
}

const model = defineModel<string>()
const emit = defineEmits(['blur'])

const props = withDefaults(defineProps<TextInputProps>(), {
  status: 'idle',
  disabled: false,
})

const inputElement = useTemplateRef<HTMLElement>('input')

watch(inputElement, _el => _el && props.autofocus ? _el.focus() : undefined)

const showPassword = ref<boolean>(false)

// monitor icons container width to add padding to input element
// thus avoiding overlaps
const { width: iconsWidth } = useElementSize(
  useTemplateRef<HTMLElement>('icons'),
  undefined,
  { box: 'border-box' },
)

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
      v-model.trim="model"
      :size="1"
      :placeholder="props.placeholder"
      :type="type"
      :disabled="props.disabled"
      :tabindex="props.tabindex"
      :autofocus="props.autofocus"
      :class="[status]"
      @blur="emit('blur')"
    >
    <div
      ref="icons"
      class="icons-wrapper"
    >
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
    border-radius: 0.4rem;
    transition: all 200ms ease-out;

    padding-right: v-bind("`max(0.6em, calc(${iconsWidth}px + 12px))`");

    &:disabled {
      background: $neutral-50;
      color: $neutral-300;
    }

    &.error {
      box-shadow: 0 0 2px $red-700;
    }
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

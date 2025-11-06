<script setup lang="ts">
import { Check, TriangleAlert } from 'lucide-vue-next'

export type LongTextInputProps = {
  placeholder?: string
  autofocus?: boolean
  tabindex?: number
  status?: 'idle' | 'pending' | 'success' | 'error'
  disabled?: boolean
}

const model = defineModel<string>('model', { default: '' })
const emit = defineEmits(['blur', 'submit'])

const props = withDefaults(defineProps<LongTextInputProps>(), {
  status: 'idle',
  disabled: false,
})

const textarea = useTemplateRef<HTMLTextAreaElement>('textarea')

// monitor icons container width to add padding to textarea element
// thus avoiding overlaps
const { width: iconsWidth } = useElementSize(
  useTemplateRef<HTMLElement>('icons'),
  undefined,
  { box: 'border-box' },
)

useTextareaAutosize({
  element: textarea,
  input: model,
  styleProp: 'minHeight',
  watch: iconsWidth,
})

watch(textarea, _el => _el && props.autofocus ? _el.focus() : undefined)

const blur = () => unref(textarea)?.blur()

function enterDown(event: KeyboardEvent) {
  // ignore keydown enter if shift is not rpressed
  if (!event.shiftKey) event.preventDefault()
}

function enterUp(event: KeyboardEvent) {
  // if shift key is pressed, handle it as a normal line return
  if (event.shiftKey) return

  event.preventDefault()
  submit()
}

function submit() {
  emit('submit', model.value ?? '')
}
</script>

<template>
  <div class="LongTextInput">
    <textarea
      ref="textarea"
      v-model="model"
      :size="1"
      :placeholder="props.placeholder"
      :disabled="props.disabled"
      :tabindex="props.tabindex"
      :autofocus="props.autofocus"
      :class="[status]"
      :rows="8"
      @blur="emit('blur')"
      @keydown.enter="enterDown"
      @keyup.enter="enterUp"
      @keyup.escape="blur();"
    />
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
    </div>
  </div>
</template>

<style scoped lang="scss">
.LongTextInput {
  @include flex-row;
  position: relative;

  textarea {

    -ms-overflow-style: none;
    scrollbar-width: none;

    &::-webkit-scrollbar {
      display: none;
    }

    width: 100%;
    resize: none;
    padding: 0.4em 0.6em;

    padding-right: v-bind("`max(0.6em, calc(${iconsWidth}px + 12px))`");

    border: 1px solid $neutral-200;
    border-radius: 8px;
    outline: none;

    font-family: 'Inter', sans-serif;
    font-size: 1em;
    transition: box-shadow 0.2s ease-out;

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

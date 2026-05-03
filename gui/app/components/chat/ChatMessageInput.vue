<script setup lang="ts">
import { Send } from 'lucide-vue-next'

const model = defineModel<string>()

// props
const props = withDefaults(
  defineProps<{
    loading?: boolean
  }>(),
  {
    loading: false,
  },
)
const { loading } = toRefs(props)

const emit = defineEmits<(e: 'submit', value: string) => void>()

const { textarea, input: autosizeInput } = useTextareaAutosize()

const input = computed({
  get: () => model.value,
  set: (newValue) => {
    model.value = newValue
    autosizeInput.value = newValue ?? ''
  },
})

const stop = watch(input, (v) => {
  input.value = v?.substring(0, 1000)
})

function blur() {
  if (textarea.value) textarea.value.blur()
}

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

const disabled = computed(
  () => model.value?.trim().length === 0 || loading.value,
)

tryOnUnmounted(stop)
</script>

<template>
  <div class="ChatMessageInput">
    <textarea
      ref="textarea"
      v-model="input"
      placeholder="Répondre"
      :disabled="loading"
      tabindex="1"
      @keydown.enter="enterDown"
      @keyup.enter="enterUp"
      @keyup.escape="blur();"
    />
    <IconButton
      class="IconButton"
      :disabled="disabled"
      @click="submit"
    >
      <transition
        name="pop"
        mode="out-in"
      >
        <LoadingAnimation
          v-if="loading"
          :small="true"
        />
        <Send
          v-else
          :size="20"
          :stroke-width="1.5"
        />
      </transition>
    </IconButton>
  </div>
</template>

<style scoped lang="scss">
.ChatMessageInput {

  @include flex-row;
  position: relative;

  textarea {
    -ms-overflow-style: none;
    scrollbar-width: none;

    &::-webkit-scrollbar {
      display: none;
    }

    width: 100%;
    height: auto;
    resize: none;

    border-radius: $radius-pill;
    border: 1px solid $divider;
    box-shadow: $shadow-sm;
    transition: box-shadow 200ms ease-out, border-color 200ms ease-out;

    line-height: 1.4;
    padding: $space-3 48px $space-3 $space-4;

    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;

    &::placeholder {
      color: $text-tertiary;
    }

    &:focus,
    &:hover {
      outline: none;
      box-shadow: $shadow-md;
    }

    &:focus {
      border-color: $neutral-400;
    }
  }

  .IconButton {
    @include flex-row-center;

    position: absolute;
    right: $space-3;
    bottom: $space-3;

    background: $primary-500;
    box-shadow: $shadow-sm;
    box-sizing: border-box;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    color: white;

    --loader-color: #fff;

    svg {
      position: relative;
      top: 1px;
      left: -1px;
    }
  }
}
</style>

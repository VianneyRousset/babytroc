<script setup lang="ts">

import { Send } from 'lucide-vue-next';

const model = defineModel<string>();

// props
const props = withDefaults(defineProps<{
  loading?: boolean,
}>(), {
  loading: false,
});
const { loading } = toRefs(props);

const emit = defineEmits<{
  (e: "submit", value: string): void
}>()

const { textarea, input: autosizeInput } = useTextareaAutosize();

const input = computed({
  get: () => model.value,
  set: (newValue) => {
    model.value = newValue
    autosizeInput.value = newValue ?? "";
  }
})

function blur() {
  if (textarea.value)
    textarea.value.blur();
}

function enterDown(event: KeyboardEvent) {

  // ignore keydown enter if shift is not rpressed
  if (!event.shiftKey)
    event.preventDefault();

}

function enterUp(event: KeyboardEvent) {

  // if shift key is pressed, handle it as a normal line return
  if (event.shiftKey)
    return;

  event.preventDefault();
  blur();
  submit();
}

function submit() {
  emit("submit", model.value ?? "");
}

</script>

<template>

  <div class="ChatMessageInput">
    <textarea ref="textarea" v-model="input" placeholder="Répondre" tabindex="1" @keydown.enter="enterDown"
      @keyup.enter="enterUp" @keyup.escape="blur();" />
    <IconButton @click="submit" class="IconButton" :disabled="true">
      <Loader v-if="loading" :small="true" />
      <Send v-else :size="20" :strokeWidth="1.5" :absoluteStrokeWidth="true" />
    </IconButton>
  </div>

</template>

<style scoped lang="scss">
.ChatMessageInput {

  @include flex-row;
  position: relative;

  padding: 1rem;

  textarea {

    -ms-overflow-style: none;
    scrollbar-width: none;

    &::-webkit-scrollbar {
      display: none;
    }

    width: 100%;

    resize: none;

    border-radius: 1rem;
    border: 1px solid $neutral-300;
    box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.2);
    transition: box-shadow 0.2s ease-out,
    all 0.2 ease-out;

    line-height: 1.2rem;
    padding-left: 1rem;
    padding-top: 1.2rem;
    padding-right: 64px;


    font-family: 'Inter',
    sans-serif;
    font-size: 1rem;

    &::placeholder {
      color: #9e9ea7;
    }

    &:focus,
    &:hover {
      outline: none;
      box-shadow: 0px 1px 8px rgba(0, 0, 0, 0.3);
    }

    &:focus {
      border: 1px solid $neutral-500;
    }
  }

  .IconButton {
    @include flex-row-center;

    position: absolute;
    right: 28px;
    bottom: 28px;

    background: $primary-500;
    box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.2);
    box-sizing: border-box;
    width: 40px;
    height: 40px;
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

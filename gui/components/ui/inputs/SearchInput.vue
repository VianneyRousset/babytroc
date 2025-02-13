<script setup lang="ts">

import { Search, X } from 'lucide-vue-next';

const model = defineModel<string>();

const emit = defineEmits<{
  (e: "submit", value: string): void
}>()

const input = ref<HTMLElement | null>(null);

function blur() {
  if (input.value)
    input.value.blur();
}

function clear() {
  model.value = "";
}

function submit() {
  emit("submit", model.value ?? "");
}

</script>

<template>

  <div>
    <Search class="search-icon" :size="20" :strokeWidth="1" :absoluteStrokeWidth="true" />
    <input v-model="model" ref="input" placeholder="Search" type="search" tabindex="1" autofocus
      @keyup.enter="blur(); submit();" @keyup.escape="blur(); clear(); submit();" />
    <X v-if="model !== ''" @click="clear(); submit();" class="x-icon" :size="20" :strokeWidth="1"
      :absoluteStrokeWidth="true" />
  </div>

</template>

<style scoped lang="scss">
div {

  @include flex-row;
  position: relative;
  flex-grow: 1;

  input {
    width: 100%;
    padding: 0.2rem 2.5rem;
  }

  svg {
    position: absolute;
    stroke: $neutral-400;

    &.search-icon {
      left: 0.7rem;
    }

    &.x-icon {
      right: 0.7rem;
      cursor: pointer;
    }
  }
}
</style>

<script setup lang="ts">

import { ChevronRight } from 'lucide-vue-next';

const props = defineProps<{
  title: string,
}>();

const open = ref(false);

const content = useTemplateRef("content");

const { width, height } = useElementSize(content)

const maxHeight = computed(() => {

  if (open.value)
    return `${height.value + 20}px`

  return '0px';
});

</script>

<template>
  <div class="fold" :class="{ 'open': open }">
    <div class="header" @click="open = !open">
      <ChevronRight style="cursor: pointer;" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      <h2>{{ props.title }}</h2>
    </div>
    <div class="container">
      <div class="content" ref="content">
        <slot />
      </div>
    </div>

  </div>
</template>

<style scoped lang="scss">
.fold {

  border-top: 1px solid $neutral-200;

  .header {

    @include flex-row;

    cursor: pointer;

    svg {
      stroke: $neutral-600;
      margin-right: 0.2rem;
      transition: transform 0.2s ease-out;
    }

    h2 {
      margin: 0.8rem 0;
    }

  }

  .container {
    padding: 0 0.8rem;
    transition: max-height 0.2s ease-out;
    overflow: hidden;
    max-height: v-bind('maxHeight');

    .content {
      margin-bottom: 20px;
    }
  }

  &.open {
    svg {
      transform: rotate(90deg);
    }
  }

}
</style>

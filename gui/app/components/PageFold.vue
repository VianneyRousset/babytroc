<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next'

const open = defineModel<boolean>()
</script>

<template>
  <CollapsibleRoot
    v-model:open="open"
    class="PageFold"
  >
    <!-- Header -->
    <CollapsibleTrigger class="header">
      <ChevronRight
        :size="32"
        :stroke-width="2"
        :absolute-stroke-width="true"
      />
      <h2>
        <slot name="title" />
      </h2>
    </CollapsibleTrigger>

    <!-- Content -->
    <CollapsibleContent class="content">
      <div>
        <slot />
      </div>
    </CollapsibleContent>
  </CollapsibleRoot>
</template>

<style scoped lang="scss">
.PageFold {

  @include flex-column;
  border-top: 1px solid $neutral-200;

  .header {

    @include reset-button;
    @include flex-row;
    width: 100%;

    cursor: pointer;

    svg {
      stroke: $neutral-600;
      margin-right: 0.2rem;
      transition: transform 0.2s ease-out;
    }

    h2 {
      margin: 0.8rem 0;
    }

    &[data-state="open"] {
      svg {
        transform: rotate(90deg);
      }
    }

  }

  .content {
    transition: max-height 0.2s ease-out;
    overflow: hidden;

    &>div {
      padding: 1rem 0.8rem;
      padding-bottom: 2rem;
    }
  }

  .content[data-state="open"] {
    animation: slideDown 300ms ease-out;
  }

  .content[data-state="closed"] {
    animation: slideUp 300ms ease-out;
  }

}

@keyframes slideDown {
  from {
    height: 0;
  }

  to {
    height: var(--radix-collapsible-content-height);
  }
}

@keyframes slideUp {
  from {
    height: var(--radix-collapsible-content-height);
  }

  to {
    height: 0;
  }
}
</style>

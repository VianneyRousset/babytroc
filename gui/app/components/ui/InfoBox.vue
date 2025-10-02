<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next'
import type { LucideIcon } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  icon?: LucideIcon
  chevronRight?: boolean
}>(), {
  chevronRight: false,
})

const { icon, chevronRight } = toRefs(props)

const slots = useSlots()
</script>

<template>
  <div class="InfoBox">
    <!-- Icon -->
    <div
      v-if="slots.icon || icon"
      class="icon with"
    >
      <component
        :is="icon"
        v-if="icon"
        :size="32"
        :stroke-width="1"
      />
      <slot name="icon" />
    </div>

    <!-- Content -->
    <div class="content">
      <slot />
    </div>

    <!-- Mini -->
    <div
      v-if="slots.mini"
      class="mini"
    >
      <slot name="mini" />
    </div>

    <!-- Chevron right -->
    <ChevronRight
      v-if="chevronRight"
      class="chevron"
      :size="32"
      :stroke-width="1"
    />
  </div>
</template>

<style scoped lang="scss">
.InfoBox {

  @include flex-row;
  justify-content: space-between;
  padding: 0.6em 0.8em;

  position: relative;

  border: 1px solid $neutral-600;
  border-radius: 0.5em;

  color: $neutral-600;
  font-weight: 500;

  &:has(.mini) {
    padding: 0.8em;
    .content {
      padding-bottom: 0.4em;
    }
  }

  .icon {
    @include flex-column;
    margin-right: 1em;
  }

  .content {
    flex: 1;
  }

  .mini {
    @include ellipsis-overflow;
    max-width: 70%;
    position: absolute;
    bottom: 0.25rem;
    right: 1rem;
    color: $neutral-400;
    font-weight: 400;
    font-size: 0.75rem;
  }

}
</style>

<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next'
import type { LucideIcon } from 'lucide-vue-next'
import type { RouteLocationGeneric } from 'vue-router'

const props = withDefaults(defineProps<{
  target?: string | RouteLocationGeneric
  icon?: LucideIcon
  chevron?: boolean
}>(), {
  chevron: false,
})

const { target, icon, chevron } = toRefs(props)

const slots = useSlots()
const NuxtLink = resolveComponent('NuxtLink')
</script>

<template>
  <component
    :is="target ? NuxtLink : 'div'"
    class="Slab"
    :to="target"
    :role="target ? undefined : 'group'"
  >
    <!-- Icon -->
    <slot name="icon">
      <component
        :is="icon"
        v-if="icon"
        :size="32"
        :stroke-width="1.5"
        aria-hidden="true"
      />
    </slot>

    <div class="title">
      <div>
        <slot />
      </div>
      <div
        v-if="slots.sub"
        class="sub"
      >
        <slot name="sub" />
      </div>
    </div>

    <div
      v-if="slots.mini"
      class="mini"
    >
      <slot name="mini" />
    </div>

    <transition
      name="pop"
      mode="in-out"
      appear
    >
      <div
        v-if="slots.badge"
        class="badge"
      >
        <slot name="badge" />
      </div>
    </transition>

    <ChevronRight
      v-if="chevron"
      :size="32"
      :stroke-width="1.5"
      aria-hidden="true"
    />
  </component>
</template>

<style scoped lang="scss">
a {
  @include reset-link;
}

.Slab {
  @include flex-row;
  gap: $space-4;
  justify-content: flex-start;
  padding: $space-4;
  position: relative;
  border: 1px solid transparent;
  transition: background 150ms ease-out;

  @include hover-only {
    background: $bg-page;
    border-color: transparent;
  }

  &:focus-visible {
    outline: 2px solid $primary-500;
    outline-offset: -2px;
    border-radius: $radius-sm;
  }

  @include touch-feedback;

  :deep(.title) {
    @include flex-column;
    align-items: stretch;
    gap: $space-1;
    flex: 1;

    font-family: "Plus Jakarta Sans", sans-serif;
    overflow: hidden;

    div {
      @include ellipsis-overflow;
      color: $text-primary;
      font-size: 0.95rem;
      font-weight: 500;

      &.sub {
        color: $text-secondary;
        font-size: 0.8125rem;
        font-weight: 400;
      }
    }
  }

  .mini {
    @include ellipsis-overflow;
    max-width: 70%;
    position: absolute;
    bottom: $space-1;
    right: $space-4;
    color: $text-tertiary;
    font-size: 0.75rem;
  }

  .badge {
    @include flex-column-center;
    background: $red-600;
    min-height: 8px;
    min-width: 8px;
    border-radius: 50%;
  }

  /* chevron */
  & > svg {
    color: $text-tertiary;
  }
}
</style>

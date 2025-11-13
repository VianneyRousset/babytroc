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
  >
    <!-- Icon -->
    <slot name="icon">
      <component
        :is="icon"
        v-if="icon"
        :size="32"
        :stroke-width="1.5"
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
    />
  </component>
</template>

<style scoped lang="scss">
a {
  @include reset-link;
}

.Slab {

  @include flex-row;
  gap: 1rem;
  justify-content: flex-start;
  padding: 1rem;
  position: relative;
  border: 1px solid transparent;

  &:hover {
    background: $neutral-50 !important;
    border-color: $neutral-200 !important;
  }

  &:active {
    background: $neutral-100 !important;
    border-color: $neutral-200 !important;
  }

  :deep(.title) {
    @include flex-column;
    align-items: stretch;
    gap: 4px;
    flex: 1;

    font-family: "Plus Jakarta Sans";
    overflow: hidden;

    div {
      @include ellipsis-overflow;
      color: $neutral-900;
      font-size: 1.4rem;

      &.sub {
        color: $neutral-400;
        font-size: 1rem;
      }
    }
  }

  .mini {
    @include ellipsis-overflow;
    max-width: 70%;
    position: absolute;
    bottom: 0.25rem;
    right: 1rem;
    color: $neutral-300;
    font-size: 0.75rem;
  }

  .badge {
    @include flex-column-center;
    background: $primary-300;
    min-height: 0.75rem;
    min-width: 0.75rem;
    border-radius: 0.5rem;
    font-size: 0.75rem;
    color: white;
  }

  /* chevron */
  &>svg {
    color: $neutral-700;
  }
}
</style>

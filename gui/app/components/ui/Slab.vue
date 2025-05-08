<script setup lang="ts">
import { ChevronRight } from "lucide-vue-next";

const slots = useSlots();
</script>

<template>
  <div class="Slab">

    <slot name="image" />

    <div class="title">
      <div>
        <slot />
      </div>
      <div v-if="slots.sub" class="sub">
        <slot name="sub" />
      </div>
    </div>

    <div v-if="slots.mini" class="mini">
      <slot name="mini" />
    </div>

    <div v-if="slots.badge" class="badge">
      <slot name="badge" />
    </div>

    <ChevronRight :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />

  </div>

</template>

<style scoped lang="scss">
.Slab {

  @include flex-row;
  gap: 1rem;
  justify-content: flex-start;
  padding: 1rem;
  position: relative;

  &:active {
    background: $neutral-100;
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
    color: $neutral-400;
  }
}
</style>

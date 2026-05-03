<script setup lang="ts">
import type { LucideIcon } from 'lucide-vue-next'
import type { RouteLocationGeneric } from 'vue-router'

const props = withDefaults(
  defineProps<{
    aspect?: 'flat' | 'outline'
    size?: 'large' | 'normal' | 'small'
    color?: 'neutral' | 'primary' | 'red'
    loading?: boolean
    timeout?: number
    disabled?: boolean
    icon?: LucideIcon
    target?: string | RouteLocationGeneric
  }>(),
  {
    aspect: 'flat',
    size: 'normal',
    color: 'neutral',
    loading: false,
    timeout: 500,
    disabled: false,
  },
)
const { aspect, size, color, loading, timeout, disabled, icon, target } = toRefs(props)

const { value: longLoading } = useThrottle(loading, timeout)

const slots = useSlots()

const iconSize = computed(() => ({ small: 16, normal: 24, large: 32 }[unref(size)]))

const classes = computed(() => ({
  large: unref(size) === 'large',
  small: unref(size) === 'small',

  flat: unref(aspect) === 'flat',
  outline: unref(aspect) === 'outline',

  disabled: unref(disabled),

  primary: unref(color) === 'primary',
  red: unref(color) === 'red',

  loading: unref(loading),
}))

const NuxtLink = resolveComponent('NuxtLink')
</script>

<template>
  <component
    :is="target ? NuxtLink : 'div'"
    class="TextButton"
    role="button"
    :class="classes"
    :to="target"
  >
    <div
      v-if="loading && longLoading"
      class="loader"
    >
      <LoadingAnimation :small="true" />
    </div>
    <div class="content">
      <div
        v-if="slots.icon || icon"
        class="icon"
      >
        <component
          :is="icon"
          v-if="icon"
          :size="iconSize"
          :stroke-width="1"
        />
        <slot name="icon" />
      </div>
      <slot />
    </div>
  </component>
</template>

<style scoped lang="scss">
.TextButton {
  @include reset-link;

  display: block;
  position: relative;
  color: white;
  text-align: center;
  cursor: pointer;
  user-select: none;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 0.95rem;
  border-radius: $radius-pill;

  padding: 0 $space-6;
  height: 40px;
  line-height: 40px;

  transition: background 200ms ease-out, border-color 200ms ease-out, color 200ms ease-out;

  --color-50: #{$neutral-50};
  --color-100: #{$neutral-100};
  --color-200: #{$neutral-200};
  --color-300: #{$neutral-300};
  --color-400: #{$neutral-400};
  --color-500: #{$neutral-500};
  --color-600: #{$neutral-600};
  --color-700: #{$neutral-700};
  --color-800: #{$neutral-800};
  --color-900: #{$neutral-900};

  .loader {
    @include flex-row-center;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
  }

  .content {
    @include flex-row;
    align-content: center;
    justify-content: center;
    gap: $space-2;

    .icon {
      display: flex;
      align-items: center;
    }
  }

  &.loading > .content {
    opacity: 0.1;
  }

  &.primary {
    --color-50: #{$primary-50};
    --color-100: #{$primary-100};
    --color-200: #{$primary-200};
    --color-300: #{$primary-300};
    --color-400: #{$primary-400};
    --color-500: #{$primary-500};
    --color-600: #{$primary-600};
    --color-700: #{$primary-700};
    --color-800: #{$primary-800};
    --color-900: #{$primary-900};
  }

  &.red {
    --color-50: #{$red-50};
    --color-100: #{$red-100};
    --color-200: #{$red-200};
    --color-300: #{$red-300};
    --color-400: #{$red-400};
    --color-500: #{$red-500};
    --color-600: #{$red-600};
    --color-700: #{$red-700};
    --color-800: #{$red-800};
    --color-900: #{$red-900};
  }

  &.small {
    height: 36px;
    line-height: 36px;
    padding: 0 $space-4;
    font-size: 0.85rem;
  }

  &.large {
    height: 48px;
    line-height: 48px;
    padding: 0 $space-8;
    font-size: 1.05rem;
  }

  &.flat {
    background: var(--color-500);

    @include hover-only {
      background: var(--color-600);
    }

    @include touch-feedback;

    &.disabled, &.loading {
      background: var(--color-100);
      color: var(--color-400);
      cursor: default;
    }
  }

  &.outline {
    color: var(--color-500);
    border: 1.5px solid var(--color-500);
    background: transparent;

    height: 37px;
    line-height: 37px;

    &.small {
      height: 33px;
      line-height: 33px;
    }

    &.large {
      height: 45px;
      line-height: 45px;
    }

    @include hover-only {
      color: var(--color-600);
      border-color: var(--color-600);
    }

    @include touch-feedback;

    &.disabled, &.loading {
      color: var(--color-200);
      border-color: var(--color-200);
      cursor: default;
    }
  }
}
</style>

<script setup lang="ts">
import { Minus } from 'lucide-vue-next'

const checked = defineModel<boolean>()

const props = withDefaults(
  defineProps<{
    size?: 'large' | 'normal'
    indeterminate?: boolean
  }>(),
  {
    size: 'normal',
    indeterminate: false,
  },
)

const { size, indeterminate } = toRefs(props)

const radixChecked = computed<boolean | 'indeterminate'>({
  get: () => unref(indeterminate) ? 'indeterminate' : (checked.value ?? false),
  set: (v) => { checked.value = v === true },
})
</script>

<template>
  <label
    class="Checkbox"
    :class="[size, { indeterminate }]"
    :checked="checked"
  >
    <CheckboxRoot
      v-model:checked="radixChecked"
      class="CheckboxRoot"
    >
      <CheckboxIndicator class="CheckboxIndicator">
        <Minus
          v-if="indeterminate"
          :size="10"
          :stroke-width="3"
        />
        <div v-else />
      </CheckboxIndicator>
    </CheckboxRoot>
    <span>
      <slot />
    </span>
  </label>
</template>

<style scoped lang="scss">
.Checkbox {

  @include flex-row;
  cursor: pointer;
  color: $text-secondary;

  &:hover {
    color: $text-primary;
  }

  &[checked="true"],
  &[checked="true"]:hover,
  &.indeterminate,
  &.indeterminate:hover {
    color: $primary-text-safe;
  }

  :deep(.CheckboxRoot) {

    @include reset-button;
    @include flex-row-center;

    cursor: pointer;
    background: $neutral-100;

    .CheckboxIndicator {
      @include flex-row-center;
      border-radius: 0.2em;
      background: $primary-400;
      width: 100%;
      height: 100%;
      color: white;
    }
  }

  &.normal {
    padding: 0.3em 0.2em;
    gap: 0.6em;

    :deep(.CheckboxRoot) {
      width: round(up, 1em, 1px);
      height: round(up, 1em, 1px);
      border-radius: round(up, 0.3em, 1px);
      padding: round(up, 0.2em, 1px);
    }
  }

  &.large {
    padding: 0.9em 0.8em;
    gap: 1em;

    border: 1px solid transparent;
    border-radius: 0.5em;

    &:hover {
      border-color: $neutral-200;
    }

    &[checked="true"] {
      background: $primary-50;
      border-color: $primary-200;
    }

    :deep(.CheckboxRoot) {

      width: round(up, 1.3em, 1px);
      height: round(up, 1.3em, 1px);
      border-radius: round(up, 0.4em, 1px);
      padding: round(up, 0.3em, 1px);

      border: 0.1em solid $neutral-300;

      &[data-state="checked"],
      &[data-state="indeterminate"] {
        background: $primary-100;
      }
    }
  }
}
</style>

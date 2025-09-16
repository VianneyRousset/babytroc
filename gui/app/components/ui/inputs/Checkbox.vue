<script setup lang="ts">
const checked = defineModel<boolean>()

const props = withDefaults(
  defineProps<{
    size?: 'large' | 'normal'
  }>(),
  {
    size: 'normal',
  },
)

const { size } = toRefs(props)
</script>

<template>
  <label
    class="Checkbox"
    :class="[size]"
    :checked="checked"
  >
    <CheckboxRoot
      v-model:checked="checked"
      class="CheckboxRoot"
    >
      <CheckboxIndicator class="CheckboxIndicator">
        <div />
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
  color: $neutral-600;

  &:hover {
    color: $neutral-900;
  }

  &[checked="true"],
  &[checked="true"]:hover {
    color: $primary-500;
  }

  :deep(.CheckboxRoot) {

    @include reset-button;
    @include flex-row-center;

    cursor: pointer;
    background: $neutral-100;

    .CheckboxIndicator {
      display: block;
      border-radius: 0.2em;
      background: $primary-400;
      width: 100%;
      height: 100%;
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

      &[data-state="checked"] {
        background: $primary-100;
      }
    }
  }
}
</style>

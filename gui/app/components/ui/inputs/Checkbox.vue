<script setup lang="ts">
const model = defineModel<boolean>()
</script>

<template>
  <label
    class="Checkbox"
    :class="{ checked: model }"
  >
    <CheckboxRoot
      v-model:checked="model"
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

  gap: 1rem;
  padding: 1rem;
  border: 1px solid transparent;
  border-radius: 0.5rem;

  font-size: 1.2rem;
  color: $neutral-700;

  &:hover {
    border-color: $neutral-200;
    color: $neutral-900;
  }

  &.checked {
    background: $primary-50;
    border-color: $primary-400;
    color: $primary-400;
  }

  :deep(.CheckboxRoot) {

    cursor: pointer;

    width: 25px;
    height: 25px;
    border-radius: 4px;
    border: 1px solid $neutral-300;
    background: $neutral-100;
    padding: 5px;

    &[data-state="checked"] {
      background: $primary-100;
    }

    .CheckboxIndicator {
      display: block;
      border-radius: 3px;
      background: $primary-400;
      width: 100%;
      height: 100%;
    }

  }
}
</style>

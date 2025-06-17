<script setup lang="ts">
const model = defineModel<boolean>()
</script>

<template>
  <transition
    name="pop"
    mode="in-out"
  >
    <div
      v-show="model"
      class="popup"
    >
      <slot />
      <div class="actions">
        <slot name="actions" />
      </div>
    </div>
  </transition>
</template>

<style scoped lang="scss">
.popup {
  @include flex-column;
  align-items: center;
  gap: 1.5rem;
  border-radius: 1rem;
  width: 60%;
  background: white;
  padding: 1.5rem;
  color: $neutral-500;
  font-size: 1.15rem;
  max-width: 300px;

  box-shadow: 0px 4px 36px rgba(0, 0, 0, 0.2);

  .actions {
    display: flex;
    flex-direction: column;
    align-self: stretch;
    align-items: stretch;
    gap: 0.5rem;
  }
}
</style>

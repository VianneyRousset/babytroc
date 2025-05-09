<script setup lang="ts">
const model = defineModel<boolean>();
</script>

<template>

  <transition name="pop" mode="in-out">
    <div class="popup" v-show="model">
      <slot />
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
  padding: 2rem 1.5rem;
  color: $neutral-500;
  font-size: 1.15rem;
  max-width: 300px;

  box-shadow: 0px 4px 36px rgba(0, 0, 0, 0.2);

  :deep(.button) {
    align-self: stretch;
  }
}
</style>

<script setup lang="ts">

const model = defineModel<boolean>();

function onKeyDown(event: KeyboardEvent) {
  if (event.key == 'Escape') {
    model.value = false;
    event.preventDefault();
  }
}

onMounted(() => window.addEventListener('keydown', onKeyDown));
onUnmounted(() => window.removeEventListener('keydown', onKeyDown));

</script>

<template>
  <div class="overlay" :class="{ open: model }" @click.self="model = false">
    <slot />
  </div>
</template>

<style scoped lang="scss">
.overlay {

  display: none;

  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 20;

  width: 100%;
  height: 100%;

  background: rgba(0, 0, 0, 0.5);

  &.open {
    display: block;
  }

}
</style>

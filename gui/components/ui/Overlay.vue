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
  <div v-show="model" class="Overlay" @click.self="model = false">
    <slot />
  </div>
</template>

<style scoped lang="scss">
.Overlay {
  @include flex-column-center;

  position: fixed;
  overflow: auto;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 50;

  height: 100vh;
  width: 100vw;

  background: rgba(0, 0, 0, 0.5);
}
</style>

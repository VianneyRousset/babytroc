<script setup lang="ts">
const value = defineModel<string>({ default: "" });
</script>

<template>
  <input
    v-model="value"
    type="text"
    name="website"
    tabindex="-1"
    autocomplete="off"
    aria-hidden="true"
    class="Honeypot"
  >
</template>

<style scoped lang="scss">
.Honeypot {
  position: absolute;
  left: -9999px;
  width: 1px;
  height: 1px;
  opacity: 0;
}
</style>

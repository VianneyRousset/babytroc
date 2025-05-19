<script setup lang="ts">
const images = defineModel<Array<string>>()
</script>

<template>
  <div class="ItemStudioImages">
    <transition
      v-for="(img, index) in images"
      :key="`img${index}`"
      name="pop"
      mode="in-out"
      appear
    >
      <div>
        <img :src="img">
      </div>
    </transition>
  </div>
</template>

<style lang="scss" scoped>
.ItemStudioImages {
  @include flex-row-center;
  gap: 16px;

  div {
    width: 48px;
    height: 48px;
    margin-bottom: 16px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 0 8px black;
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
}
</style>

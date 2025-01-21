<script setup lang="ts">

const props = defineProps<{
  images: string[]
}>();

const containerRef = ref(null)
const swiper = useSwiper(containerRef, {
  effect: 'creative',
  spaceBetween: 10,
  grabCursor: true,
  rewind: true,
})

</script>

<template>
  <div>
    <ClientOnly>

      <swiper-container ref="containerRef" @click="swiper.next()" :pagination="true" :grabsCursor="true"
        class="container">
        <swiper-slide v-for="(image, idx) in props.images" :key="idx"
          :style="{ backgroundImage: `url(/api/v1/images/${image})` }">
          <div :style="`background-image: `"></div>
        </swiper-slide>
      </swiper-container>

      <!-- loader -->
      <template #fallback>
        <div class="container loading">
          <Loader />
        </div>
      </template>

    </ClientOnly>
  </div>
</template>

<style scoped lang="scss">
.container {

  --swiper-theme-color: rgba(0, 0, 0, 0.6);

  border-radius: 1rem;
  overflow: hidden;
  background: $neutral-100;
  aspect-ratio: 1;

  &.loading {
    @include flex-row;
    justify-content: center;
  }

  swiper-slide {
    aspect-ratio: 1;
    background-repeat: no-repeat;
    background-size: cover;
    background-position: center;
  }
}
</style>

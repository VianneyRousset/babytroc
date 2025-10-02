<script setup lang="ts">
import 'vue3-carousel/carousel.css'
import { Carousel, Slide, Pagination, Navigation } from 'vue3-carousel'

const props = defineProps<{
  images: string[]
}>()

const { images } = toRefs(props)

function onKeyDown(event: KeyboardEvent) {
  const element = event.target as HTMLElement

  if (element.tagName === 'INPUT')
    return

  switch (event.key) {
    case 'ArrowLeft':
      // swiper.prev()
      break
    case 'ArrowRight':
      // swiper.next()
      break
  }
}

onMounted(() => window.addEventListener('keydown', onKeyDown))
onUnmounted(() => window.removeEventListener('keydown', onKeyDown))

const carouselConfig = {
  itemsToShow: 1,
  wrapAround: true,

  gap: 10,
}
</script>

<template>
  <Carousel
    class="ImageGallery"
    v-bind="carouselConfig"
  >
    <Slide
      v-for="(image, idx) in images"
      :key="idx"
    >
      <img
        class="carousel__item"
        :src="image"
      >
    </Slide>

    <template #addons>
      <Navigation />
      <Pagination />
    </template>
  </Carousel>
</template>

<style scoped lang="scss">
.ImageGallery {
  border-radius: 1em;
  overflow: hidden;

  img {
    display: block;
    width: 100%;
    height: 100%;
    aspect-ratio: 1;
    object-fit: cover;
  }
}
</style>

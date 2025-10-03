<script setup lang="ts">
import 'vue3-carousel/carousel.css'
import { Carousel, Slide, Pagination, Navigation } from 'vue3-carousel'
import type { ComponentProps } from 'vue-component-type-helpers'

type CarouselConfig = ComponentProps<typeof Carousel>

const props = withDefaults(defineProps<{
  images: string[]
  config?: CarouselConfig
}>(), {
  config: () => ({}),
})

const { images, config } = toRefs(props)

const carousel = useTemplateRef<typeof Carousel>('carousel')

function onKeyDown(event: KeyboardEvent) {
  const element = event.target as HTMLElement

  if (element.tagName === 'INPUT')
    return

  switch (event.key) {
    case 'ArrowLeft':
      unref(carousel)?.prev()
      break
    case 'ArrowRight':
      unref(carousel)?.next()
      break
  }
}

onMounted(() => window.addEventListener('keydown', onKeyDown))
onUnmounted(() => window.removeEventListener('keydown', onKeyDown))

const carouselConfig = {
  itemsToShow: 2.5,
  wrapAround: true,

  gap: 10,
  ...unref(config),
}
</script>

<template>
  <Carousel
    ref="carousel"
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

  .carousel__slide {

    transition: opacity 200ms ease-out;

    &:not(.carousel__slide--active) {
      opacity: 0.5;
    }
  }
}
</style>

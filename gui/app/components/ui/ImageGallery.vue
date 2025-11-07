<script setup lang="ts">
import 'vue3-carousel/carousel.css'
import { Image, Pencil } from 'lucide-vue-next'
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

const empty = computed(() => unref(images).length === 0)

const carouselConfig = computed(() => ({
  itemsToShow: 2.5,
  wrapAround: !unref(empty),
  enabled: !unref(empty),

  gap: 10,
  ...unref(config),
}))
</script>

<template>
  <div
    class="ImageGallery"
    @click="() => console.log('click')"
  >
    <Carousel
      ref="carousel"
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

      <Slide v-if="empty">
        <div class="empty">
          <Image
            :size="128"
            :stroke-width="1"
          />
          <div>Aucune image disponible</div>
        </div>
      </Slide>

      <template #addons>
        <Navigation v-if="images.length > 0" />
        <Pagination v-if="images.length > 0" />
      </template>
    </Carousel>
    <div class="edit">
      <FloatingToggle
        :icon="Pencil"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.ImageGallery {
  border-radius: 1em;
  overflow: hidden;
  position: relative;

  img {
    display: block;
    width: 100%;
    height: 100%;
    aspect-ratio: 1;
    object-fit: cover;
  }

  .edit {
    @include flex-column-center;
    position: absolute;
    top: 1em;
    right: 1em;
    cursor: pointer;
    z-index: 2;
    aspect-ratio: 1;
    border-radius: 50%;
    /* box-shadow: 0 0 1em black; */
    filter: drop-shadow(0 0 12px black);


    &:hover svg {
      filter: drop-shadow(0 0 12px $neutral-200);
    }
  }

  .empty {
    @include flex-column-center;
    gap: 1em;

    width: 100%;
    height: 100%;
    aspect-ratio: 1;
    background: $neutral-100;
    border-radius: 1em;
    border: 1px solid $neutral-300;

    color: $neutral-300;
    font-size: 1.5em;
    font-weight: 600;

    & > svg {
      width: 40%;
      height: 40%;
    }

    & > div {
      width: 40%;
      text-align: center;
    }
  }

  .carousel__slide {

    transition: opacity 200ms ease-out;

    &:not(.carousel__slide--active) {
      opacity: 0.5;
    }
  }
}
</style>

<script setup lang="ts">
import 'vue3-carousel/carousel.css'
import { Image, Pencil } from 'lucide-vue-next'
import { Carousel, Slide, Pagination, Navigation } from 'vue3-carousel'
import type { ComponentProps } from 'vue-component-type-helpers'

type CarouselConfig = ComponentProps<typeof Carousel>

const emit = defineEmits(['edit'])

const props = withDefaults(defineProps<{
  images: string[]
  config?: CarouselConfig
  editable?: boolean
}>(), {
  config: () => ({}),
  editable: false,
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
  <div class="ImageGallery">
    <Carousel
      ref="carousel"
      v-bind="carouselConfig"
    >
      <Slide
        v-for="(image, idx) in images"
        :key="idx"
      >
        <ProgressiveImage
          class="carousel__item"
          :name="image"
        />
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
    <div
      v-if="editable"
      class="edit"
      @click="() => emit('edit')"
    >
      <FloatingToggle
        :icon="Pencil"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.ImageGallery {
  border-radius: $radius-lg;
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
    top: $space-4;
    right: $space-4;
    cursor: pointer;
    z-index: 2;
    aspect-ratio: 1;
    border-radius: 50%;

    @include hover-only {
      svg {
        filter: drop-shadow(0 0 12px rgba(255, 255, 255, 0.6));
      }
    }
  }

  .empty {
    @include flex-column-center;
    gap: $space-4;

    width: 100%;
    height: 100%;
    aspect-ratio: 1;
    background: white;

    color: $text-tertiary;
    font-size: 1rem;
    font-weight: 500;

    & > svg {
      width: 30%;
      height: 30%;
    }

    & > div {
      width: 40%;
      text-align: center;
    }
  }

  .carousel__slide {
    transition: opacity 200ms ease-out;
    aspect-ratio: 1;

    &:not(.carousel__slide--active) {
      opacity: 0.5;
    }
  }
}
</style>

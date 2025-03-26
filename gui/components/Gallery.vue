<script setup lang="ts">

const props = defineProps<{
  images: string[],
}>();

const { images } = toRefs(props);

const containerRef = ref(null)
const swiper = useSwiper(containerRef, {
  effect: 'creative',
  spaceBetween: 10,
  grabCursor: true,
  rewind: true,
})

function onKeyDown(event: KeyboardEvent) {
  switch (event.key) {
    case 'ArrowLeft':
      swiper.prev();
      break;
    case 'ArrowRight':
      swiper.next();
      break;
  }

  event.preventDefault();
}

onMounted(() => window.addEventListener('keydown', onKeyDown));
onUnmounted(() => window.removeEventListener('keydown', onKeyDown));

</script>

<template>
  <div class="Gallery">
    <swiper-container ref="containerRef" @click="swiper.next()" :pagination="true" :grabsCursor="true">
      <swiper-slide v-for="(image, idx) in images" :key="idx">
        <AspectRatio :ratio="1">
          <img :src="image">
        </AspectRatio>
      </swiper-slide>
    </swiper-container>
  </div>
</template>

<style scoped lang="scss">
.Gallery {

  aspect-ratio: 1;
  border-radius: 1rem;
  overflow: hidden;

  swiper-container {
    --swiper-theme-color: rgba(0, 0, 0, 0.6);

    swiper-slide {
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
    }
  }
}
</style>

<script setup lang="ts">

const props = withDefaults(defineProps<{
  images: string[],
  loading?: boolean,
}>(), {
  loading: false,
});

const { images, loading } = toRefs(props);

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

    <ClientOnly>

      <!-- loader -->
      <ContentLoader v-if="loading" viewBox="0 0 24 24">

        <path
          d="M 0,0 V 24 H 24 V 0 Z m 10.25,9.5 h 3.5 c 0.411176,0 0.75,0.338824 0.75,0.75 v 3.5 c 0,0.411176 -0.338824,0.75 -0.75,0.75 h -3.5 C 9.838824,14.5 9.5,14.161176 9.5,13.75 v -3.5 C 9.5,9.838824 9.838824,9.5 10.25,9.5 Z m 0,0.5 C 10.107176,10 10,10.107176 10,10.25 v 3.5 c 0,0.142824 0.107176,0.25 0.25,0.25 h 0.146484 l 2.198243,-2.198242 c 0.145391,-0.145348 0.337844,-0.218262 0.530273,-0.218262 0.192429,0 0.384882,0.07291 0.530274,0.218262 L 14,12.146484 V 10.25 C 14,10.107176 13.892824,10 13.75,10 Z m 1,0.5 c 0.411253,0 0.75,0.338748 0.75,0.75 0,0.411252 -0.338747,0.75 -0.75,0.75 -0.411252,0 -0.75,-0.338748 -0.75,-0.75 0,-0.411252 0.338748,-0.75 0.75,-0.75 z m 0,0.5 C 11.108968,11 11,11.108968 11,11.25 c 0,0.141032 0.108968,0.25 0.25,0.25 0.141032,0 0.25,-0.108968 0.25,-0.25 C 11.5,11.108968 11.391032,11 11.25,11 Z M 14,12.853515 13.301758,12.155273 c -0.09972,-0.09969 -0.253799,-0.09969 -0.353516,0 L 11.103516,14 H 13.75 C 13.892824,14 14,13.892824 14,13.75 Z" />
      </ContentLoader>


      <!-- Gallery -->
      <swiper-container v-else ref="containerRef" @click="swiper.next()" :pagination="true" :grabsCursor="true"
        class="container">
        <swiper-slide v-for="(image, idx) in images" :key="idx"
          :style="{ backgroundImage: `url(/api/v1/images/${image})` }">
          <div :style="`background-image: `"></div>
        </swiper-slide>
      </swiper-container>

    </ClientOnly>
  </div>
</template>

<style scoped lang="scss">
.Gallery {

  aspect-ratio: 1;
  border-radius: 1rem;
  overflow: hidden;

  .container {

    --swiper-theme-color: rgba(0, 0, 0, 0.6);


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
}
</style>

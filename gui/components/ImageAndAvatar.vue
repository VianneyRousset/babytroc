<script setup lang="ts">

// TODO query reduced image size

const props = defineProps<{
  image: string | null,
  avatar: string | null,
}>();

const { image, avatar } = toRefs(props);

const imageStyle = computed(() => ({
  backgroundImage: `url('/api/v1/images/${props.image}')`,
}));


</script>

<template>
  <div class="ImageAndAvatar">

    <div class="image">
      <AspectRatio :ratio="1">
        <img v-if="image" class="h-full w-full object-cover" :src="image">
      </AspectRatio>
    </div>

    <Avatar :seed="avatar" :size="32" />

  </div>
</template>

<style scoped lang="scss">
.ImageAndAvatar {

  @include flex-row;

  position: relative;
  width: 64px;
  width: 64px;

  .image {
    width: 64px;
    height: 64px;
    background: $neutral-100;

    overflow: hidden;
    border-radius: 0.5rem;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .Avatar {
    position: absolute;
    bottom: -10px;
    right: -10px;
  }

}
</style>

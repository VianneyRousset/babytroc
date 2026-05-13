<script setup lang="ts">
const props = defineProps<{
	imageName: string | null;
	avatar: string | null;
}>();

const { imageName, avatar } = toRefs(props);

const image = computed(() => {
	const name = unref(imageName);
	return name ? imagePath(name, 256) : null;
});
</script>

<template>
  <div class="ImageAndAvatar">
    <div class="image">
      <AspectRatio :ratio="1">
        <img
          v-if="image"
          :src="image"
        >
      </AspectRatio>
    </div>

    <UserAvatar
      :seed="avatar"
      :size="32"
    />
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

  .UserAvatar {
    position: absolute;
    bottom: -10px;
    right: -10px;
  }

}
</style>

<script setup lang="ts">

// TODO query reduced image size
// TODO "missing image" if item.image is missing

import type { ApiResponse, ApiRequestQuery } from '#open-fetch'

type Chat = ApiResponse<'list_client_chats_v1_me_chats_get'>[number];
type ChatQuery = ApiRequestQuery<'list_client_chats_v1_me_chats_get'>;

const props = defineProps<{
  image: string,
  avatar: string,
}>();

const imageStyle = computed(() => ({
  backgroundImage: `url('/api/v1/images/${props.image}')`,
}));


</script>

<template>
  <div class="box">
    <div class="image" :style="imageStyle">
      <!-- <Avatar :item="props.avatar" :size="36" />-->
    </div>
  </div>
</template>

<style scoped lang="scss">
.box {
  @include flex-row;

  .image {
    position: relative;
    width: 64px;
    aspect-ratio: 1;
    border-radius: 0.5rem;

    background-repeat: no-repeat;
    background-size: cover;
    background-position: center;

    &>* {
      border-radius: 50%;
      box-shadow: 0px 0px 4px rgba(0, 0, 0, 0.5);
      position: absolute;
      bottom: -10px;
      right: -10px;
    }
  }
}
</style>

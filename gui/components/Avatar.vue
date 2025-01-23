<script setup lang="ts">

import { onMounted, ref } from 'vue';
import { createAvatar } from '@dicebear/core';
import { thumbs } from '@dicebear/collection';

const props = defineProps<{
  seed?: string,
}>();

const avatar = createAvatar(thumbs, {
  seed: "weloifjwoiegfjew",
  size: 64,
  scale: 80,
  radius: 50,
  backgroundColor: ["c4d6c5"],
  shapeColor: ["729577"],
}).toDataUri();

</script>

<template>
  <div>
    <img :src="avatar">
  </div>
</template>

<script setup lang="ts">

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
  size: {
    type: Number,
    required: true,
  }
});

</script>

<template>
  <img
    :src="`https://api.dicebear.com/7.x/thumbs/svg?seed=${props.user.id}&size=${size}&scale=80&radius=50&backgroundColor=9ec8b9&shapeColor=88ab8e`" />
</template>

<style scoped></style>

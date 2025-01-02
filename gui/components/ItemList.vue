<script setup lang="ts">

const props = defineProps({
  items: {
    type: String,
    required: true,
  },
});

</script>

<template>
  <div>
    {{ items }}
  </div>
</template>

<style scoped lang="scss"></style>

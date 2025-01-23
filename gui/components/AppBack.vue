<script setup lang="ts">

import { ArrowLeft } from 'lucide-vue-next';

const props = defineProps<{
  fallback: string,
}>();

const routeStack = useRouteStack();

const targetRoute = computed(() => routeStack.previous.value ?? props.fallback);

async function onclick() {
  routeStack.pop();
  routeStack.pop();
}

</script>

<template>

  <NuxtLink :to="targetRoute" @click="onclick">
    <ArrowLeft style="cursor: pointer;" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
  </NuxtLink>

</template>

<style scoped lang="scss">
a {
  @include reset-link;
}
</style>

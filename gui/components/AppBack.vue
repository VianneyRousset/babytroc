<script setup lang="ts">

import { ArrowLeft } from 'lucide-vue-next';

const route = useRoute();

const props = defineProps<{
  fallback?: string,
}>();

const routeStack = useRouteStack();

const defaultFallback = computed(() => "/" + route.fullPath.split("/").filter(e => e)[0]);

const targetRoute = computed(() => routeStack.previous.value ?? props.fallback ?? defaultFallback.value);

async function onclick() {
  routeStack.markBackward();
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

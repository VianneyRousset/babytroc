<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'

const props = defineProps<{
  fallback?: string
}>()

const { fallback } = toRefs(props)

const routeStack = useRouteStack()

const { currentTabRoot } = useTab()
const targetRoute = computed(
  () => routeStack.previous.value ?? unref(fallback) ?? currentTabRoot,
)

async function onclick() {
  routeStack.markBackward()
  routeStack.pop()
  routeStack.pop()
}
</script>

<template>
  <NuxtLink
    :to="targetRoute"
    @click="onclick"
  >
    <ArrowLeft
      style="cursor: pointer;"
      :size="32"
      :stroke-width="2"
    />
  </NuxtLink>
</template>

<style scoped lang="scss">
a {
  @include reset-link;
}
</style>

<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'

const props = defineProps<{
  fallback?: string
}>()

const { fallback } = toRefs(props)

const { previous, goBack } = useNavigation()

const { currentTabRoot } = useTab()
const targetRoute = computed(
  () => unref(previous) ?? unref(fallback) ?? currentTabRoot,
)
</script>

<template>
  <NuxtLink
    :to="targetRoute"
    class="AppBack"
    @click="goBack"
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

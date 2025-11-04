<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'

const props = defineProps<{
  fallback?: string
}>()

const { fallback } = toRefs(props)

const { goBack } = useNavigation()
</script>

<template>
  <ArrowLeft
    style="cursor: pointer;"
    :size="32"
    :stroke-width="2"
    @click="() => goBack(fallback)"
  />
</template>

<style scoped lang="scss">
a {
  @include reset-link;
}
</style>

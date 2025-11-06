<script setup lang="ts">
import { ArrowLeft } from 'lucide-vue-next'

const props = defineProps<{
  fallback?: string
}>()

const { fallback } = toRefs(props)

const { goBack } = useNavigation()
</script>

<template>
  <IconButton
    :icon="ArrowLeft"
    @click="() => goBack(fallback)"
  />
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  loading?: boolean
}>(), {
  loading: false,
})

const { loading } = toRefs(props)
</script>

<template>
  <transition
    name="fade"
    mode="out-in"
    appear
  >
    <LoadingAnimation v-if="loading" />
    <slot v-else />
  </transition>
</template>

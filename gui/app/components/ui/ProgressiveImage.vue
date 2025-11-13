<script setup lang="ts">
const props = defineProps<{
  src: string
  placeholderSrc: string
}>()

const { src, placeholderSrc } = toRefs(props)

const { data: imageData, status } = useQuery({
  key: () => ['image', unref(src)],
  query: async () => {
    const request = new Request(unref(src))
    const resp: Response = await fetch(request)
    return URL.createObjectURL(await resp.blob())
  },
})

const placeholder = computed(() => unref(status) !== 'success')
const _src = computed(() => unref(placeholder) ? unref(placeholderSrc) : unref(imageData))
</script>

<template>
  <img
    :src="_src"
    :class="{ placeholder }"
  >
</template>

<style scoped lang="scss">
img {

  transition: filter 200ms ease-out;
  filter: blur(0px);

  &.placeholder {
    filter: blur(12px);
  }
}
</style>

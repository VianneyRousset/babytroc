<script setup lang="ts">
definePageMeta({
  layout: 'studio',
})

const store = useItemEditStore('create')

const images = ref(store.images.images.map(img => img.copy()))

const { goBack } = useNavigation()

async function save() {
  store.images.setImages(unref(images))
  navigateTo('/me/items/new')
}
</script>

<template>
  <AppPage custom-styling>
    <ItemStudio
      v-model="images"
      @exit="goBack"
      @done="() => { save(); goBack() }"
    />
  </AppPage>
</template>

<style scoped lang="scss">
.AppPage {
  position: fixed;
  overflow: hidden;
  width: 100%;
  height: 100%;

  .ItemStudio {
    width: 100%;
    height: 100%;
  }
}
</style>

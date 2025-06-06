<script setup lang="ts">
import { X } from 'lucide-vue-next'

const studioImagesUploadStore = useStudioImagesUploadStore('newitem')

watch(() => studioImagesUploadStore.data, images => console.log(toRaw(images)))
</script>

<template>
  <div>
    <ItemStudio
      v-model="studioImagesUploadStore.images"
      @done="console.log('done')"
    >
      <template #header>
        <NuxtLink
          to="/home"
        >
          <X
            style="cursor: pointer;"
            :size="32"
            :stroke-width="2"
            @click="navigateTo('/home')"
          />
        </NuxtLink>
        <h1>Nouvel objet</h1>
      </template>
    </ItemStudio>
  </div>
</template>

<style lang="scss" scoped>
.ItemImagesStudio {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 20;
}
</style>

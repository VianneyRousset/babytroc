<script setup lang="ts">
import { Trash2, Crop } from 'lucide-vue-next'

const img = defineModel<StudioImage>()
const emit = defineEmits(['delete', 'crop'])
</script>

<template>
  <div
    class="ItemStudioImageView"
  >
    <transition
      name="fade"
      mode="in-out"
      appear
    >
      <img
        :src="img?.cropped"
        draggable="false"
      >
    </transition>

    <transition
      name="pop"
      mode="in-out"
      appear
    >
      <IconButton
        class="delete"
        style="transition-delay: 0.1s"
        @click="emit('delete')"
      >
        <Trash2
          :size="24"
          :stroke-width="1.33"
        />
      </IconButton>
    </transition>
    <transition
      name="pop"
      mode="in-out"
      appear
    >
      <IconButton
        class="crop"
        style="transition-delay: 0.2s"
        @click="emit('crop')"
      >
        <Crop
          :size="24"
          :stroke-width="1.33"
        />
        <div>Recadrer</div>
      </IconButton>
    </transition>
  </div>
</template>

<style lang="scss" scoped>
.ItemStudioImageView {
  position: relative;

  img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .IconButton {
    position: absolute;
    color: white;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 20px;
    height: 40px;
    width: 40px;
    cursor: pointer;

    &.delete {
      top: 1rem;
      lefT: 1rem;
    }

    &.crop {
      gap: 0.5rem;
      padding: 0 10px;
      left: 0;
      right: 0;
      bottom: 1rem;
      margin-inline: auto;
      width: fit-content;
    }
  }
}
</style>

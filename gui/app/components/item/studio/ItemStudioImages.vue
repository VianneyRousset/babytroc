<script setup lang="ts">
import draggable from 'vuedraggable'

const images = defineModel<Array<StudioImage>>()

const dragging = ref(false)
</script>

<template>
  <draggable
    v-model="images"
    class="ItemStudioImages"
    :component-data="{
      tag: 'ul',
    }"
    :animation="200"
    ghost-class="ghost"
    item-key="id"
  >
    <template #item="{ element }">
      <transition
        name="pop"
        mode="in-out"
        appear
      >
        <li class="list-group-item">
          <img :src="element.cropped">
        </li>
      </transition>
    </template>
  </draggable>
</template>

<style lang="scss" scoped>
.ItemStudioImages {
  @include flex-row-center;
  flex-wrap: wrap;
  gap: 16px;
  margin: 16px;

  li {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 0 8px black;
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .ghost {
    opacity: 0.5;
    background: #c8ebfb;
  }
}
</style>

<script setup lang="ts">
import { Plus } from 'lucide-vue-next'
import draggable from 'vuedraggable'

const images = defineModel<Array<StudioImage>>()

const props = defineProps<{
  selected?: number
}>()

const { selected } = toRefs(props)

const emit = defineEmits<(e: 'select', id: number | undefined) => void>()

function select(event: { item: HTMLElement }) {
  const id = Number.parseInt(event.item.getAttribute('element-id') ?? '')
  emit('select', isNaN(id) ? undefined : id)
}
</script>

<template>
  <draggable
    v-model="images"
    class="ItemStudioImages"
    tag="ul"
    :animation="200"
    ghost-class="ghost"
    item-key="id"
    @choose="select"
    @start="select"
  >
    <template #item="{ element }">
      <transition
        name="pop"
        mode="in-out"
        appear
      >
        <li
          class="list-group-item"
          :class="{ selected: selected === element.id }"
          :element-id="element.id"
        >
          <img :src="element.cropped">
        </li>
      </transition>
    </template>
    <template #footer>
      <li
        class="add"
        :class="{ selected: selected == null }"
        @click="emit('select', undefined)"
      >
        <Plus
          :size="24"
          :stroke-width="2"
        />
      </li>
    </template>
  </draggable>
</template>

<style lang="scss" scoped>
.ItemStudioImages {
  @include flex-row-center;
  @include reset-list;
  flex-wrap: wrap;
  font-size: clamp(10px, 4vw, 24px);
  gap: 0.8em;
  margin: 1em;

  li {
    width: 2em;
    height: 2em;
    border-radius: 0.5em;
    overflow: hidden;
    box-shadow: 0 0 8px black;
    border: 3px solid transparent;
    cursor: pointer;

    &.selected {
      border: 3px solid $primary-400;
      box-shadow: 0 0 8px black;
    }

    &.add {
      @include flex-column-center;
      color: $neutral-400;
    }

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

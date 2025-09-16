<script setup lang="ts" generic="T extends ItemPreview">
import { Heart, Bookmark, Clock } from 'lucide-vue-next'

// TODO query reduced image size
// TODO "missing image" if item.image is missing

const props = defineProps<{
  item: T
}>()

const { item } = toRefs(props)

const { formatedTargetedAgeMonths } = useItemTargetedAgeMonths(item)
const { firstImagePath } = useItemFirstImage(item)

const backgroundImage = computed(() => {
  const backgrounds = []
  const params = ''

  backgrounds.push('linear-gradient(transparent 0 40%, #202020 100%)')
  backgrounds.push(`url('${unref(firstImagePath)}${params}')`)

  return backgrounds.join(', ')
})
</script>

<template>
  <div
    class="ItemCard"
    :style="{ backgroundImage: backgroundImage }"
  >
    <div class="status">
      <Heart
        v-if="item.liked"
        class="liked"
        :size="24"
        :stroke-width="2"
      />
      <Bookmark
        v-if="item.saved"
        class="saved"
        :size="24"
        :stroke-width="2"
      />
      <Clock
        v-if="!item.available"
        class="not-available"
        :size="24"
        :stroke-width="2"
      />
    </div>

    <div class="info">
      <div class="age">
        {{ formatedTargetedAgeMonths }}
      </div>
      <div class="name">
        {{ item.name }}
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.ItemCard {
  display: flex;
  box-sizing: border-box;
  aspect-ratio: 1;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 1em;
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  cursor: pointer;
  color: $neutral-50;

  &:target {
    /* ensure the target element (anchor) is not flushed to the top */
    scroll-margin-top: 20vh;
    animation: flash;
    animation-duration: 0.8s;
  }

  .status {
    display: flex;
    gap: 1em;
    justify-content: right;
    padding: 1em;

    svg {
      filter: drop-shadow(0px 0px 3px rgba(0, 0, 0, 0.5));
    }

    .not-available {
      color: $neutral-100;
    }

    .liked,
    .saved {
      color: $neutral-100;
      fill: $neutral-100;
    }

  }

  .info {
    padding: 1em;

    .age {
      color: $primary-300;
      margin-bottom: 0.2em;
    }

    .name {
      font-family: "Plus Jakarta Sans", sans-serif;
      color: var(--brand-50);
      font-size: 1.6em;
      font-weight: bold;
    }
  }
}
</style>

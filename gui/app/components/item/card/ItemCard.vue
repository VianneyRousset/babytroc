<script setup lang="ts" generic="T extends ItemPreview">
import { Heart, Clock } from 'lucide-vue-next'
import type { RouteLocationGeneric } from 'vue-router'

// TODO "missing image" if item.image is missing

const props = defineProps<{
  item: T
  target?: string | RouteLocationGeneric
}>()

const { item } = toRefs(props)

const { formatedTargetedAgeMonths } = useItemTargetedAgeMonths(item)
const { firstImageName } = useItemFirstImage(item)

const backgroundImage = computed(() => {
  const backgrounds = []

  backgrounds.push('linear-gradient(transparent 0 40%, #202020 100%)')
  backgrounds.push(`url('${imagePath(unref(firstImageName), 512)}')`)
  backgrounds.push(`url('${imagePath(unref(firstImageName), 128)}')`)

  return backgrounds.join(', ')
})

const NuxtLink = resolveComponent('NuxtLink')
</script>

<template>
  <component
    :is="target ? NuxtLink : 'div'"
    class="ItemCard"
    :style="{ backgroundImage }"
    :to="target"
  >
    <div class="status">
      <Heart
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
  </component>
</template>

<style scoped lang="scss">
a {
  @include reset-link;
}

.ItemCard {
  display: flex;
  box-sizing: border-box;
  aspect-ratio: 1;
  flex-direction: column;
  justify-content: space-between;
  border-radius: $radius-lg;
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  cursor: pointer;
  color: $neutral-50;
  overflow: hidden;
  transition: box-shadow 200ms ease-out;

  @include hover-only {
    box-shadow: $shadow-md;
  }

  @include touch-feedback;

  &:target {
    scroll-margin-top: 20vh;
  }

  .status {
    display: flex;
    gap: $space-3;
    justify-content: right;
    padding: $space-3;

    svg {
      filter: drop-shadow(0px 0px 3px rgba(0, 0, 0, 0.5));
    }

    .not-available {
      color: $neutral-100;
    }

    .saved {
      color: $neutral-100;
      fill: $neutral-100;
    }
  }

  .info {
    padding: $space-3 $space-4;
    background: linear-gradient(transparent, rgba(0, 0, 0, 0.5));

    .age {
      color: $primary-300;
      font-size: 0.78rem;
      font-weight: 500;
      margin-bottom: $space-1;
    }

    .name {
      @include font-jakarta;
      @include ellipsis-overflow;
      color: white;
      font-size: 1.1em;
      font-weight: 600;
    }
  }
}
</style>

<script setup lang="ts">

import { Heart, Bookmark, Clock } from 'lucide-vue-next';

// TODO query reduced image size
// TODO "missing image" if item.image is missing

const props = defineProps<{
  item: ItemPreview,
  likedItems: Array<Item | ItemPreview>,
  savedItems: Array<Item | ItemPreview>,
}>();
const { item, likedItems, savedItems } = toRefs(props);

const { formatedTargetedAgeMonths } = useItemTargetedAgeMonths(item);
const { firstImagePath } = useItemFirstImage(item);
const { isLikedByUser } = useItemLike(item, likedItems);
const { isSavedByUser } = useItemSave(item, savedItems);

const backgroundImage = computed(() => {

  const backgrounds = []
  const params = "";

  backgrounds.push("linear-gradient(transparent 0 40%, #202020 100%)");
  backgrounds.push(`url('${unref(firstImagePath)}${params}')`);

  return backgrounds.join(", ");

});


</script>

<template>
  <aspectRatio :ratio="1">
    <div class="ItemCard" :style="{ backgroundImage: backgroundImage }">

      <div class="status">
        <Heart v-if="isLikedByUser" class="liked" :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" />
        <Bookmark v-if="isSavedByUser" class="saved" :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" />
        <Clock v-if="!item.available" class="not-available" :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" />
      </div>

      <div class="info">
        <div class="age">{{ formatedTargetedAgeMonths }}
        </div>
        <div class="name">{{ item.name }}</div>
      </div>
    </div>
  </AspectRatio>

</template>

<style scoped lang="scss">
.ItemCard {
  display: flex;
  box-sizing: border-box;
  aspect-ratio: 1;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 1rem;
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
    gap: 1rem;
    justify-content: right;
    padding: 1rem;

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
    padding: 1rem;

    .age {
      color: $primary-300;
      margin-bottom: 0.2em;
    }

    .name {
      font-family: "Plus Jakarta Sans", sans-serif;
      color: var(--brand-50);
      font-size: 1.6rem;
      font-weight: bold;
    }
  }
}
</style>

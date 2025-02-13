<script setup lang="ts">

import { OctagonAlert } from 'lucide-vue-next';

const props = withDefaults(defineProps<{
  end: boolean,
  empty?: boolean,
  error?: boolean,
  loading?: boolean,
}>(), {
  empty: false,
  error: false,
  loading: true,
});

/*
useInfiniteScroll(
  useTemplateRef("container"),
  () => {

    if (props.loading || props.end) {
      console.log("loadMore -> nope");
      return;
    }

    console.log("loadMore -> yep");
    emit("more");
  },
  {
    distance: props.distance,
  }
)
*/

</script>

<template>
  <div>

    <slot />

    <!-- loading -->
    <div v-if="props.loading" class="loader">
      <Loader />
    </div>

    <!-- extra items fetch error -->
    <div v-else-if="props.error" class="error">
      <OctagonAlert :size="24" :strokeWidth="2" :absoluteStrokeWidth="true" />
      <slot name="error" />
    </div>

    <!-- no items -->
    <div v-else-if="!props.loading && props.empty" class="empty">
      <slot name="empty" />
    </div>

  </div>
</template>

<style lang="scss" scoped>
.loader {
  @include flex-row-center;
  margin-top: 2em;
  margin-bottom: 2em;
}

.error {
  @include flex-row;
  justify-content: center;
  gap: 1rem;
  margin-top: 2em;
  color: $red-700;
}

.empty {
  margin-top: 2em;
  color: $neutral-300;
  text-align: center;
}
</style>

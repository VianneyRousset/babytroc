<script setup lang="ts">

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
  targetPrefix: {
    type: String,
    required: true,
  },
});

</script>

<template>
  <div class="navigator">
    <ItemPreview class="item" v-for="item in items" :key="item.id" :item="item" :id="`item-${item.id}`"
      :statuses="{ ok: !item.activeLoan, nok: !!item.activeLoan, tag: item?._count?.loanRequests }"
      @select="navigateTo(`${targetPrefix}${item.id}`);" imageSize=512 showInfo clickable />
  </div>
</template>

<style scoped>
.navigator {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 2rem;
}

.item {
  height: 24rem;
  flex-shrink: 0;
  flex-grow: 1;
}

@media only screen and (max-width: 55rem) {
  .navigator {
    grid-template-columns: 1fr 1fr;
  }
}

@media only screen and (max-width: 45rem) {
  .navigator {
    grid-template-columns: 1fr;
  }
}
</style>

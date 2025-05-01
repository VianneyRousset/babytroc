<script setup lang="ts">
import { Heart } from "lucide-vue-next";

import type { AsyncStatus } from "@pinia/colada";

const props = defineProps<{item: Item}>();

const { item } = toRefs(props);

const { formatedTargetedAgeMonths } = useItemTargetedAgeMonths(item);
const { regions, regionsIds } = useItemRegions(item);
</script>

<template>
  <div class="ItemDescriptionAndDetails">
    <Fold>
      <template v-slot:title>Description</template>
      <div class="name">{{ item.name }}</div>
      <div>{{ item.description }}</div>
    </Fold>
    <Fold>
      <template v-slot:title>Détails</template>
      <div class="minitable">
        <div class="label">Âge</div>
        <div>{{ formatedTargetedAgeMonths }}</div>
        <div class="label">Régions</div>
        <ul>
          <li v-for="region in regions">{{ region.name }}</li>
        </ul>
      </div>
      <RegionsMap :modelValue="regionsIds" />
    </Fold>
  </div>
</template>

<style lang="scss" scoped>
.name {
  font-weight: 600;
  margin-bottom: 0.8rem;
  color: $neutral-500;
}
</style>

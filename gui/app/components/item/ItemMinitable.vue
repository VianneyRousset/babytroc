<script setup lang="ts" generic="T extends { targeted_age_months: string, region_ids: number[] }">
const props = defineProps<{ item: T }>();

const { item } = toRefs(props);

const { regionIds } = useItemRegions(item);
const { regions: allRegions } = useRegionsList();

const _regions = computed(() =>
	(unref(allRegions) ?? []).filter((r) => unref(regionIds).has(r.id)),
);
</script>

<template>
  <Minitable class="ItemMinitable">
    <div class="label">
      Âge
    </div>
    <ItemAge :item="item" />
    <div class="label">
      Régions
    </div>
    <ul>
      <li
        v-for="region in regions"
        :key="`region${region.id}`"
      >
        {{ region.name }}
      </li>
    </ul>
  </Minitable>
</template>

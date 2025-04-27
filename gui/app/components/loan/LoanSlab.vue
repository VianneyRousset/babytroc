<script setup lang="ts">
import { ChevronRight } from "lucide-vue-next";

const props = defineProps<{
	loan: Loan;
}>();

// loan
const { loan } = toRefs(props);

// item image
const { firstImagePath: itemImage } = useItemFirstImage(() => unref(loan).item);

// date range
const formatedDuring = computed(() =>
	formatRelativeDateRange(loan.value.during),
);
</script>

<template>
  <Slab>

    {{ loan.item.name }}

    <template #image>
      <ImageAndAvatar :image="itemImage" :avatar="loan.owner.avatar_seed" />
    </template>

    <template #sub>
      Emprunté à {{ loan.owner.name }}
    </template>

    <template #mini>
      {{ formatedDuring }}
    </template>

  </Slab>
</template>

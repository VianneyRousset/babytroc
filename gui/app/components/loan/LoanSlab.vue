<script setup lang="ts">
import type { RouteLocationGeneric } from "vue-router";

const props = withDefaults(
	defineProps<{
		loan: Loan;
		target?: string | RouteLocationGeneric;
		chevron?: boolean;
		perspective?: "borrower" | "owner";
	}>(),
	{
		chevron: false,
		perspective: "borrower",
	},
);

const { loan } = toRefs(props);

const { firstImageName: itemImageName } = useItemFirstImage(
	() => unref(loan).item,
);

const formatedDuring = computed(() =>
	formatRelativeDateRange(loan.value.during),
);

const otherUser = computed(() =>
	props.perspective === "borrower" ? unref(loan).owner : unref(loan).borrower,
);

const subLabel = computed(() =>
	props.perspective === "borrower"
		? `Emprunté à ${otherUser.value.name}`
		: `Prêté à ${otherUser.value.name}`,
);
</script>

<template>
  <Slab
    :target="target"
    :chevron="chevron"
  >
    {{ loan.item.name }}

    <template #icon>
      <ImageAndAvatar
        :image-name="itemImageName"
        :avatar="otherUser.avatar_seed"
      />
    </template>

    <template #sub>
      {{ subLabel }}
    </template>

    <template #mini>
      {{ formatedDuring }}
    </template>
  </Slab>
</template>

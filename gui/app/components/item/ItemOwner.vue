<script setup lang="ts" generic="T extends { owner: UserPreview }">
import type { ComponentProps } from "vue-component-type-helpers";
import type { UserCard } from "#components";

const props = defineProps<{
	item: T;
	target?: ComponentProps<typeof UserCard>["target"];
}>();

const { item } = toRefs(props);

const { user } = useUser({ userId: () => unref(item).owner.id });
</script>

<template>
  <UserCard
    :user="user ?? item.owner"
    :target="target"
  />
</template>

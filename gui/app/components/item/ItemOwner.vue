<script setup lang="ts" generic="T extends { owner: UserPreview }">
const props = defineProps<{ item: T }>()

const { item } = toRefs(props)

const { user } = useUser({ userId: () => unref(item).owner.id })
</script>

<template>
  <UserCard
    class="ItemOwner"
    :user="user ?? item.owner"
  />
</template>

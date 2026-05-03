<script setup lang="ts">
import type { RouteLocationGeneric } from 'vue-router'

const props = withDefaults(defineProps<{
  loan: Loan
  target?: string | RouteLocationGeneric
  chevron?: boolean
}>(), {
  chevron: false,
})

// loan
const { loan } = toRefs(props)

// item image
const { firstImagePath: itemImage } = useItemFirstImage(() => unref(loan).item)

// date range
const formatedDuring = computed(() =>
  formatRelativeDateRange(loan.value.during),
)
</script>

<template>
  <Slab
    :target="target"
    :chevron="chevron"
  >
    {{ loan.item.name }}

    <template #icon>
      <ImageAndAvatar
        :image="itemImage"
        :avatar="loan.owner.avatar_seed"
      />
    </template>

    <template #sub>
      Emprunté à {{ loan.owner.name }}
    </template>

    <template #mini>
      {{ formatedDuring }}
    </template>
  </Slab>
</template>

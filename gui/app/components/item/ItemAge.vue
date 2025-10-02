<script setup lang="ts" generic="T extends { targeted_age_months: string }">
const props = withDefaults(defineProps<{
  item: T
  lowercase?: boolean
  prefix?: string
}>(), {
  lowercase: false,
  prefix: '',
})

const { item, lowercase, prefix } = toRefs(props)

const { formatedTargetedAgeMonths: age } = useItemTargetedAgeMonths(item)

const text = computed(() => unref(lowercase) ? unref(age).toLowerCase() : unref(age))
</script>

<template>
  <div class="ItemAge">
    {{ prefix }}{{ text }}
  </div>
</template>

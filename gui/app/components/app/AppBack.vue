<script setup lang="ts">
const props = defineProps<{
	fallback?: string;
}>();

const { fallback } = toRefs(props);

const { goBack } = useNavigation();
</script>

<template>
  <IconButton
    :icon="ArrowLeft"
    @click="() => goBack(fallback)"
  />
</template>

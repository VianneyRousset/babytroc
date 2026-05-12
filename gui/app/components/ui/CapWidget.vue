<script setup lang="ts">
const props = withDefaults(
	defineProps<{
		apiUrl: string;
		siteKey: string;
		disabled?: boolean;
		resetSignal?: number | string;
	}>(),
	{
		disabled: false,
		resetSignal: 0,
	},
);

const emit = defineEmits<{
	(e: "solve", token: string): void;
	(e: "expire"): void;
}>();

const { apiUrl, siteKey, disabled, resetSignal } = toRefs(props);

const endpoint = computed(
	() => `${unref(apiUrl).replace(/\/$/, "")}/${unref(siteKey)}/`,
);

useHead({
	script: [
		{
			src: "https://cdn.jsdelivr.net/npm/cap-widget",
			key: "cap-widget-script",
			tagPosition: "bodyClose",
		},
	],
});

const el = useTemplateRef<CapWidgetElement>("el");

function onSolve(event: Event) {
	if (unref(disabled)) return;
	const detail = (event as CapSolveEvent).detail;
	emit("solve", detail.token);
}

function onExpire() {
	if (unref(disabled)) return;
	emit("expire");
}

onMounted(() => {
	const node = unref(el);
	if (node == null) return;
	node.addEventListener("solve", onSolve);
	node.addEventListener("expire", onExpire);
});

onBeforeUnmount(() => {
	const node = unref(el);
	if (node == null) return;
	node.removeEventListener("solve", onSolve);
	node.removeEventListener("expire", onExpire);
});

watch(resetSignal, () => {
	const node = unref(el);
	node?.reset?.();
});
</script>

<template>
  <div class="CapWidget">
    <cap-widget
      ref="el"
      :data-cap-api-endpoint="endpoint"
      :disabled="disabled || undefined"
    />
  </div>
</template>

<style scoped lang="scss">
.CapWidget {
  @include flex-row;
  justify-content: center;
}
</style>

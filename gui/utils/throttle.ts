// The returned ref is set to true if the given `value` is kept true for `time` ms
export function throttleTrue(value: Ref<boolean>, time: number): Ref<boolean> {
	const result = ref(false);

	let timeout = null as null | ReturnType<typeof setTimeout>;

	watch(value, (v) => {
		if (v) {
			timeout = setTimeout(() => {
				result.value = true;
			}, time);
		} else {
			if (timeout) clearTimeout(timeout);

			result.value = false;
		}
	});

	return result;
}

export function useTab() {
	const route = useRoute();
	const currentTab = route.fullPath.split("/").filter((e) => e)[0];
	const currentTabRoot = `/${currentTab}`;

	return {
		currentTab,
		currentTabRoot,
	};
}

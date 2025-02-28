function useTab() {
  const route = useRoute();
  const currentTab: Ref<string> = computed(() => route.fullPath.split("/").filter(e => e)[0]);
  const currentTabRoot: Ref<string> = computed(() => "/" + currentTab.value);

  return {
    currentTab,
    currentTabRoot,
  }
}

export { useTab }

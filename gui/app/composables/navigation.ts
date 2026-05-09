import type { Ref } from "vue";
import type {
	RouteLocationAsPathGeneric,
	RouteLocationAsRelativeGeneric,
} from "vue-router";

export type AppSection = "explore" | "saved" | "newitem" | "chats" | "me";

export function useNavigation() {
	const route = useRoute();
	const router = useRouter();
	const direction = useNuxtApp().$routeChangeDirection;
	const { currentTabRoot } = useTab();

	const appSectionUrls = new Map<AppSection, string>([
		["explore", "/explore"],
		["saved", "/saved"],
		["chats", "/chats"],
		["newitem", "/me/items/new"],
		["me", "/me"],
	]);

	const activeAppSection: Ref<AppSection> = computed(() => {
		const res = [...appSectionUrls].find(([_, v]) => route.path.startsWith(v));

		if (res == null)
			throw new Error(`Invalid app section for url '${route.path}'.`);

		return res[0] as AppSection;
	});

	function goBack(
		fallback?:
			| string
			| RouteLocationAsRelativeGeneric
			| RouteLocationAsPathGeneric
			| null,
	) {
		if (route.meta.appBack === false) return;

		// If there's browser history, go back
		if (window.history.state.back) {
			return router.go(-1);
		}

		// No history (direct URL entry, first page) — use fallback
		const resolvedFallback =
			fallback ??
			(typeof route.meta.appBack === "string" ||
			(typeof route.meta.appBack === "object" && route.meta.appBack !== null)
				? (route.meta.appBack as
						| string
						| RouteLocationAsRelativeGeneric
						| RouteLocationAsPathGeneric)
				: undefined) ??
			unref(currentTabRoot);

		return router.push(resolvedFallback);
	}

	return {
		appSectionUrls,
		activeAppSection,
		direction,
		goBack,
	};
}

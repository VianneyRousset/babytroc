import type {
	RouteLocationAsPathGeneric,
	RouteLocationAsRelativeGeneric,
} from "vue-router";

declare module "#app" {
	interface PageMeta {
		appBack?:
			| boolean
			| string
			| RouteLocationAsRelativeGeneric
			| RouteLocationAsPathGeneric;
		appTitle?: string;
	}
}

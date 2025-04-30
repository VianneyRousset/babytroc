import {
	useQueryCache,
	type DataState,
	type DataState_Success,
	type UseQueryOptions,
	type UseQueryReturn,
} from "@pinia/colada";
import { StatusCodes } from "http-status-codes";

export function useAuth() {
	const { $api } = useNuxtApp();

	const { data: me, status: meStatus } = useQuery({
		key: () => ["auth"],
		query: () =>
			$api("/v1/me", {
				onResponse: async (ctx) => {
					if (ctx.response.status === StatusCodes.UNAUTHORIZED) {
						console.log("GOT UNAUTHORIZED");
						ctx.error = undefined;
						ctx.response = new Response("null");
						console.log("response set to null");
					}
				},
			}),
	});

	// login
	async function login(email: string, password: string) {
		// create form data
		const formData = new FormData();
		formData.append("grant_type", "password");
		formData.append("username", email);
		formData.append("password", password);

		// try to login to api
		await $api("/v1/auth/login", {
			method: "POST",

			// @ts-expect-error: cannot type FormData
			body: formData,
		}).then(() => {
			const queryCache = useQueryCache();
			localStorage.setItem("auth-session", "true");
			console.log("Invalidate cache");
			queryCache.invalidateQueries({ key: ["me"] });
			queryCache.invalidateQueries({ key: ["auth"] });
		});
	}

	// logout
	async function logout() {
		await $api("/v1/auth/logout", {
			method: "POST",
		}).then(async () => {
			const queryCache = useQueryCache();
			localStorage.removeItem("auth-session");
			console.log("Invalidate cache");
			queryCache.invalidateQueries({ key: ["auth"], exact: true });
		});
	}

	return {
		login,
		logout,
		loggedIn: computed(() => {
			if (unref(meStatus) === "pending") return undefined;
			return unref(me) != null;
		}),
		loggedInStatus: meStatus,
	};
}

export function useQueryWithAuth<
	TResult,
	TError,
	TDataInitial extends TResult | undefined = undefined,
>(
	options: UseQueryOptions<TResult, TError, TDataInitial>,
): UseQueryReturn<TResult, TError, TDataInitial> {
	const { loggedIn } = useAuth();

	const { state, ...queryResult } = useQuery<TResult, TError, TDataInitial>({
		enabled: () => unref(loggedIn) === true,
		...options,
	});

	const modifiedState = computed<DataState<TResult, TError, TDataInitial>>(
		() => {
			const _state = unref(state);

			if (unref(loggedIn) === true) return _state;

			return {
				status: "success",
				data: undefined as TResult,
				error: null,
			} satisfies DataState_Success<TResult>;
		},
	);

	return {
		...queryResult,
		state: modifiedState,

		status: computed(() => unref(modifiedState).status),
		data: computed(() => unref(modifiedState).data),
		error: computed(() => unref(modifiedState).error),

		isPending: computed(() => unref(modifiedState).status === "pending"),
	};
}

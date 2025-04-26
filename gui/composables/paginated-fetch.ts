import { parseLinkHeader } from "@web3-storage/parse-link-header";

import type { paths as ApiPaths } from "#open-fetch-schemas/api";
import type { AsyncDataRequestStatus } from "#app";

import type { FetchError, FetchOptions, FetchResponse } from "ofetch";

import type { MultiWatchSources } from "vue";

import type {
	ErrorResponse,
	MediaType,
	OperationRequestBodyContent,
	ResponseObjectMap,
	SuccessResponse,
} from "openapi-typescript-helpers";

// taken from nuxt-open-fetch
type FetchResponseData<T extends Record<string | number, any>> =
	SuccessResponse<ResponseObjectMap<T>, MediaType>;
export type FetchResponseError<T extends Record<string | number, any>> =
	FetchError<ErrorResponse<ResponseObjectMap<T>, MediaType>>;
type ParamsOption<T> = T extends { parameters?: any; query?: any }
	? T["parameters"]
	: Record<string, never>;
type RequestBodyOption<T> = OperationRequestBodyContent<T> extends never
	? { body?: never }
	: undefined extends OperationRequestBodyContent<T>
		? { body?: OperationRequestBodyContent<T> }
		: { body: OperationRequestBodyContent<T> };
type ComputedOptions<T> = {
	[K in keyof T]: T[K] extends Function
		? T[K]
		: ComputedOptions<T[K]> | Ref<T[K]> | T[K];
};

export type usePaginatedFetch<ValT, ErrorT> = {
	data: Ref<Array<ValT>>;
	more: () => Promise<void>;
	reset: () => void;
	end: Ref<boolean>;
	error: Ref<ErrorT | null>;
	status: Ref<AsyncDataRequestStatus>;
};

// filter api paths that have query parameters and array-like response data
// TODO would be nice to specify the next link header
type PaginatedPaths = {
	[K in keyof ApiPaths as ApiPaths[K] extends {
		get: {
			parameters: {
				query?: infer Q;
			};
		};
	}
		? Q extends never
			? never
			: FetchResponseData<ApiPaths[K]["get"]> extends Array<any>
				? K
				: never
		: never]: ApiPaths[K];
};

type PaginatedSourceOptions<Operation> = ComputedOptions<
	ParamsOption<Operation>
> &
	ComputedOptions<RequestBodyOption<Operation>> &
	Omit<FetchOptions, "query" | "body" | "method"> & {
		watch?: MultiWatchSources | false;
	};

function usePaginatedFetch<
	ReqT extends Extract<keyof PaginatedPaths, string>,
	Operation extends Record<string | number, any> = PaginatedPaths[ReqT]["get"],
	ResT extends Array<any> = FetchResponseData<Operation>,
	ErrorT = FetchResponseError<Operation>,
	ValT = ResT[number],
>(
	url: ReqT,
	options: PaginatedSourceOptions<Operation>,
): usePaginatedFetch<ValT, ErrorT> {
	const { $api } = useNuxtApp();

	const $paginatedApi = $api as (
		url: ReqT,
		options?: PaginatedSourceOptions<Operation>,
	) => Promise<ResT>;

	// accumulates fetched data
	const data: Ref<Array<ValT>> = ref([]);

	// fetching status
	const status = ref<AsyncDataRequestStatus>("idle");

	// store fetching errors
	const error: Ref<ErrorT | null> = ref(null);

	// true if last page has been reached
	const end = ref<boolean>(false);

	// store the query params for the next query
	var cursorQuery: Partial<PaginatedSourceOptions<Operation>["query"]> = {};

	let controller: AbortController | undefined;

	function reset() {
		// abort current fetching and create a new abort controller
		controller?.abort?.("reset");
		controller =
			typeof AbortController !== "undefined"
				? new AbortController()
				: ({} as AbortController);

		// reset data, end indicator, cursor query and status
		data.value = [];
		end.value = false;
		cursorQuery = {};
		status.value = "idle";
	}

	reset();

	// fetch extra data
	async function more() {
		if (controller === undefined) throw "Uninitialized controller.";

		// skip if data is still loading
		if (status.value === "pending") return;

		// update status
		status.value = "pending";

		// fetch new data
		await $paginatedApi(url, {
			...options,
			query: {
				...options.query,
				...cursorQuery,
			},

			// signal to abort fetching
			signal: controller.signal,

			// extract next cursor query parameters from response headers
			async onResponse({
				response: { headers },
			}: { response: FetchResponse<ResT> }) {
				const linkHeader = parseLinkHeader(headers.get("link"));

				if (linkHeader === null)
					return console.error("Null linkHeader when fetching first items.");

				const { rel, url, ...query } = linkHeader.next;
				cursorQuery = query as typeof cursorQuery;
			},
		})
			.then((newData) => {
				// append new data to accumulated data
				data.value = data.value.concat(newData);

				// update end indicator and status
				end.value = newData.length == 0;
				status.value = "success";
			})
			.catch((err) => {
				if (err.cause === "reset") return;

				// update end indicator and status
				end.value = true;
				status.value = "error";

				throw err;
			});
	}

	const { watch: _watch, immediate, deep, dedupe, ...fetchOptions } = options;

	const _fetchOptions = reactive(fetchOptions);

	// trigger reset on fetch options change
	options.watch = _watch === false ? [] : [_fetchOptions, ...(_watch || [])];
	const hasScope = getCurrentScope();
	if (options.watch) {
		const unsub = watch(options.watch, () => reset());
		if (hasScope) {
			onScopeDispose(unsub);
		}
	}

	return {
		data,
		more,
		error,
		end,
		reset,
		status,
	};
}

export { usePaginatedFetch };

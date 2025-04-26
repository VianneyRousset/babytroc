import type { AsyncDataRequestStatus } from "#app";
import type { FetchError } from "ofetch";

export type {
	Chat,
	ChatQuery,
	ChatMessage,
	ChatMessageQuery,
	ChatMessageOrigin,
	ChatMessageChunk,
	ChatMessageDateGroup,
} from "./chat";
export type { Item } from "./item";
export type { Loan, LoanRequest } from "./loan";
export type { User, UserPreview } from "./user";

declare global {
	// region
	type Region = Item["regions"][0];

	interface PaginatedSource<T> {
		data: Array<T>;
		more: () => Promise<void>;
		reset: () => void;
		end: boolean;
		error: FetchError | null;
		status: AsyncDataRequestStatus;
	}
}

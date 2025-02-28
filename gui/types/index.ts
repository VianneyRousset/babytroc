import type { AsyncDataRequestStatus } from '#app';
import type { FetchError } from 'ofetch';
import type { ApiResponse, ApiRequestQuery } from '#open-fetch'

export { };

declare global {

  // chat
  type Chat = ApiResponse<'list_client_chats_v1_me_chats_get'>[number];
  type ChatQuery = ApiRequestQuery<'list_client_chats_v1_me_chats_get'>;

  // user
  type User = ApiResponse<"get_user_v1_users__user_id__get">;
  type UserPreview = Chat["borrower" | "owner"];

  // item
  type Item = ApiResponse<'get_item_v1_items__item_id__get'>;
  type ItemPreview = ApiResponse<'list_items_v1_items_get'>[number];
  type ItemQuery = ApiRequestQuery<'list_items_v1_items_get'>;

  // region
  type Region = Item["regions"][0];

  type PaginatedSource<T> = {
    data: Array<T>,
    more: () => Promise<void>,
    reset: () => void,
    end: boolean,
    error: FetchError | null,
    status: AsyncDataRequestStatus
  }

}

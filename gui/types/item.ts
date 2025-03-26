import type { ApiResponse, ApiRequestQuery } from '#open-fetch'

declare global {
  type Item = ApiResponse<'get_item_v1_items__item_id__get'>;
  type ItemPreview = ApiResponse<'list_items_v1_items_get'>[number];
  type ItemQuery = ApiRequestQuery<'list_items_v1_items_get'>;
}

export type { Item, ItemPreview, ItemQuery };

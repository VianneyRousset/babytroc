import type { ApiResponse, ApiRequestQuery, ApiRequestBody } from '#open-fetch'

declare global {
type Item = ApiResponse<'get_item_v1_items__item_id__get'>
type ItemPreview = ApiResponse<'list_items_v1_items_get'>[number]
type ItemCreate = ApiRequestBody<'create_client_item_v1_me_items_post'>
type ItemQuery = ApiRequestQuery<'list_items_v1_items_get'>
type Age = number | null
type AgeRange = [Age, Age]
}

export type { Item, ItemPreview, ItemQuery }

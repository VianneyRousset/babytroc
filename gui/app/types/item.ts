import type { ApiResponse, ApiRequestQuery, ApiRequestBody } from '#open-fetch'

export { ItemQueryAvailability } from '#build/types/open-fetch/schemas/api'
export type { ItemQueryAvailability as ItemQueryAvailabilityType } from '#build/types/open-fetch/schemas/api'

export type Item = ApiResponse<'get_item_v1_items__item_id__get'>
export type ItemPreview = ApiResponse<'list_items_v1_items_get'>[number]
export type ItemCreate = ApiRequestBody<'create_client_item_v1_me_items_post'>
export type ItemUpdate = ApiRequestBody<'update_client_item_v1_me_items__item_id__post'>
export type ItemQueryParams = ApiRequestQuery<'list_items_v1_items_get'>
export type Age = number | null
export type AgeRange = [Age, Age]
export type Region = ApiResponse<'list_regions_v1_utils_regions_get'>[number]

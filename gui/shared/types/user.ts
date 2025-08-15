import type { ApiResponse, ApiRequestBody } from '#open-fetch'

export type User = ApiResponse<'get_user_v1_users__user_id__get'>
export type UserPreview = Chat['borrower' | 'owner']
export type UserPrivate = ApiResponse<'get_client_user_v1_me_get'>
export type UserCreate = ApiRequestBody<'create_user_v1_auth_new_post'>

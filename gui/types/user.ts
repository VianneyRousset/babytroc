import type { ApiResponse, ApiRequestBody } from '#open-fetch'

declare global {
type User = ApiResponse<'get_user_v1_users__user_id__get'>
type UserPreview = Chat['borrower' | 'owner']
type UserPrivate = ApiResponse<'get_client_user_v1_me_get'>
type UserCreate = ApiRequestBody<'create_user_v1_auth_new_post'>
}

export type { User, UserPreview, UserPrivate, UserCreate }

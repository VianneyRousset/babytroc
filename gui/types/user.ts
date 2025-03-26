import type { ApiResponse } from '#open-fetch'

declare global {
  type User = ApiResponse<"get_user_v1_users__user_id__get">;
  type UserPreview = Chat["borrower" | "owner"];
}

export type { User, UserPreview };

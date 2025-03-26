import type { ApiResponse } from '#open-fetch'

declare global {
  type LoanRequest = ApiResponse<'list_client_borrowing_loan_requests_v1_me_borrowings_requests_get'>[number];
}

export type { LoanRequest };

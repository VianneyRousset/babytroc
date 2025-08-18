import type { ApiRequestBody } from '#open-fetch'
import type { components } from '#build/types/open-fetch/schemas/api'

export type Loan = components['schemas']['LoanRead']
export type LoanRequest = components['schemas']['LoanRequestRead']

export type LoanQuery = ApiRequestBody<'list_client_borrowings_v1_me_borrowings_get'>

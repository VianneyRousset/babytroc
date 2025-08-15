import type { ApiRequestBody } from '#open-fetch'
import type { components } from '#build/types/open-fetch/schemas/api'

declare global {
type Loan = components['schemas']['LoanRead']
type LoanRequest = components['schemas']['LoanRequestRead']

type LoanQuery = ApiRequestBody<'list_client_borrowings_v1_me_borrowings_get'>
}

export type { Loan, LoanRequest }

import type { components } from "#build/types/open-fetch/schemas/api";

declare global {
	type Loan = components["schemas"]["LoanRead"];
	type LoanRequest = components["schemas"]["LoanRequestRead"];
}

export type { Loan, LoanRequest };

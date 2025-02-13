import type { AsyncDataRequestStatus } from '#app';
import type { FetchError } from 'ofetch';

export { };

declare global {

  type PaginatedSource<T> = {
    data: Array<T>,
    more: () => Promise<void>,
    reset: () => void,
    end: boolean,
    error: FetchError | null,
    status: AsyncDataRequestStatus
  }
}

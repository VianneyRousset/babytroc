import { parseLinkHeader } from '@web3-storage/parse-link-header'

export function extractNextQueryParamsFromHeaders(headers: Headers) {
  const linkHeader = parseLinkHeader(headers.get('link'))

  if (!linkHeader?.next)
    return undefined

  const { rel, url, ...query } = linkHeader.next
  return query
}

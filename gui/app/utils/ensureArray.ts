import type { LocationQuery } from 'vue-router'

function getQueryParamAsArray(
  query: LocationQuery,
  paramName: string,
): Array<string> {
  const param = query[paramName]

  if (param === undefined) return []

  if (Array.isArray(param)) return param.map(String)

  return [String(param)]
}

export { getQueryParamAsArray }

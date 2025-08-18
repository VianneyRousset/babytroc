import { DateTime } from 'luxon'

export function formatTargetedAge(
  ageMin: Age,
  ageMax: Age,
): string {
  if (ageMin !== null && ageMin > 0) {
    if (ageMax === null) return `À partie de ${ageMin} mois`

    return `De ${ageMin} à ${ageMax} mois`
  }

  if (ageMax !== null) return `Jusqu'à ${ageMax} mois`

  return 'Pour tous âges'
}

export function range2string(range: Array<number | null>): string {
  return `${range[0] ?? ''}-${range[1] ?? ''}`
}

export function string2range(range: string): AgeRange {
  const { 0: lowerStr, 1: upperStr } = { ...range.split('-') }

  if (lowerStr === undefined || upperStr === undefined)
    throw new Error(`Failed to parse range "${range}"..`)

  function parseIntWithError(x: string): number {
    const num = Number.parseInt(x)
    if (num === undefined) throw new Error(`Failed to parse "${x}" into int.`)
    return num
  }

  return [
    lowerStr.length > 0 ? parseIntWithError(lowerStr) : null,
    upperStr.length > 0 ? parseIntWithError(upperStr) : null,
  ]
}

export function ensureDateTime(datetime: DateTime | string): DateTime
export function ensureDateTime(
  datetime: DateTime | string | null,
): DateTime | null
export function ensureDateTime(
  datetime: DateTime | string | null,
): DateTime | null {
  if (datetime === null) return null

  if (typeof datetime === 'string')
    return DateTime.fromISO(datetime).setLocale('fr-CH')

  return datetime
}

export function formatRelativeDate(datetime: DateTime | string): string {
  const _datetime = ensureDateTime(datetime)

  const now = DateTime.local().setLocale('fr-CH')

  if (_datetime.hasSame(now, 'day')) return 'Aujourd\'hui'

  if (_datetime.hasSame(now.minus({ days: 1 }), 'day')) return 'Hier'

  if (_datetime.hasSame(now, 'year'))
    return _datetime.toLocaleString({ month: 'long', day: 'numeric' })

  return _datetime.toFormat('DDD')
}

export function formatRelativeDateRange(
  dateRange: [DateTime | string | null, DateTime | string | null],
): string {
  const start = ensureDateTime(dateRange[0])
  const end = ensureDateTime(dateRange[1])

  const now = DateTime.local().setLocale('fr-CH')

  if (start !== null) {
    // both start and end are finite
    if (end !== null) {
      if (start > end) throw new Error('Unsorted date range')

      // same start and end date
      if (start.hasSame(end, 'day')) {
        if (start.hasSame(now, 'day')) return 'Aujourd\'hui'

        if (start.hasSame(now.minus({ days: 1 }), 'day')) return 'Hier'

        if (start.hasSame(now, 'year'))
          return `Le ${start.toLocaleString({ month: 'long', day: 'numeric' })}`

        return `Le ${start.toFormat('DDD')}`
      }

      // same start and end month
      if (start.hasSame(now, 'month')) {
        if (start.hasSame(now, 'year'))
          return `Du ${start.toFormat('d')} au ${end.toFormat('d')} ${end.toFormat('MMMM')}`
        return `Du ${start.toFormat('d')} au ${end.toFormat('d')} ${end.toFormat('MMMM yyyy')}`
      }

      // same start and end year
      if (start.hasSame(now, 'year')) {
        if (start.hasSame(now, 'year'))
          return `Du ${start.toFormat('d')} au ${end.toFormat('d')} ${end.toFormat('MMMM')}`
        return `Du ${start.toFormat('d')} au ${end.toFormat('d')} ${end.toFormat('MMMM yyyy')}`
      }

      return `Du ${start.toFormat('DDD')} au ${end.toFormat('DDD')}`
    }

    // no end date

    if (start.hasSame(now, 'day')) return 'Depuis aujourd\'hui'

    if (start.hasSame(now.minus({ days: 1 }), 'day')) return 'Depuis hier'

    if (start.hasSame(now, 'year'))
      return `Depuis le ${start.toLocaleString({ month: 'long', day: 'numeric' })}`

    return `Depuis le ${start.toFormat('DDD')}`
  }

  // no start date
  // with end date
  if (end !== null) {
    if (end.hasSame(now, 'day')) return 'Jusqu\'à aujourd\'hui'

    if (end.hasSame(now.minus({ days: 1 }), 'day')) return 'Jusqu\'a hier'

    if (end.hasSame(now, 'year'))
      return `Jusqu'au ${end.toLocaleString({ month: 'long', day: 'numeric' })}`

    return `Jusqu'au ${end.toFormat('DDD')}`
  }

  return 'Jamais'
}

const consecutiveWhitespacesRegex = /[ ]{2,}/g

export function avoidConsecutiveWhitespaces(str: string): string {
  return str.replace(consecutiveWhitespacesRegex, ' ')
}

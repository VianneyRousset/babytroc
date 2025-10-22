export function verifyChatIdFormat(str: string): boolean {
  return str.match(/^\d+-\d+$/) != null
}

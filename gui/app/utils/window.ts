export function closeWindow() {
  return window.open('', '_self')?.close()
}

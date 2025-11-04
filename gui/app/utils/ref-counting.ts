export class RefCounter<T> {
  counter: number = 0
  value: T | undefined
  readonly init: () => T
  readonly exit: (value: T) => void

  constructor(
    init: () => T,
    exit: (value: T) => void,
  ) {
    this.init = init
    this.exit = exit
  }

  start(): T {
    if (this.counter++ === 0)
      this.value = this.init()

    if (this.value == null)
      throw new Error('RefCounter value is undefined in refcounter start')

    return this.value
  }

  stop(): void {
    if (this.value == null)
      throw new Error('RefCounter value is undefined in refcounter stop')

    if (--this.counter === 0) {
      this.exit(this.value)
      this.value = undefined
    }
  }
}

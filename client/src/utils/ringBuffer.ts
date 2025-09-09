// https://www.tuckerleach.com/blog/ring-buffer
export default class RingBuffer<T> {
  private length: number
  private readonly capacity: number

  private buffer: T[]
  private headPos: number

  constructor(capacity: number) {
    this.capacity = capacity
    this.buffer = new Array(this.capacity)
    this.length = 0
    this.headPos = 0
  }

  push(item: T): void {
    if (this.isFull()) {
      throw new Error("Buffer is full")
    }

    const newheadPos = mod(this.headPos - 1, this.capacity)
    this.buffer[newheadPos] = item
    this.length++
    this.headPos = newheadPos
  }

  pop(): T | undefined {
    if (this.isEmpty()) {
      return undefined
    }

    const tailIdx = this.getTailPos()
    const lastEl = this.buffer[tailIdx]
    this.buffer[tailIdx] = undefined as T
    this.length--

    return lastEl
  }

  clear(): void {
    this.length = 0
    this.buffer = new Array(this.capacity)
  }

  isFull(): boolean {
    return this.length === this.capacity
  }

  isEmpty(): boolean {
    return this.length === 0
  }

  getLength(): number {
    return this.length
  }

  getCapacity(): number {
    return this.capacity
  }

  getItems(): T[] {
    const items = []

    const max = this.headPos + this.length - 1
    for (let i = max; i >= this.headPos; i--) {
      const tmpIdx = i % this.capacity
      items.push(this.buffer[tmpIdx])
    }

    return items
  }

  private getTailPos(): number {
    return mod(this.headPos + this.length - 1, this.capacity)
  }
}

function mod(n: number, m: number): number {
  return ((n % m) + m) % m
}

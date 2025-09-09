import { useState } from "react"

export function useLocalStorage<T>(
  key: string,
  defaultValue: T
): [T, (val: T) => void] {
  const [value, setValue] = useState<T>(() => {
    const stored = localStorage.getItem(key)
    if (stored !== null) {
      try {
        return JSON.parse(stored)
      } catch {
        return defaultValue
      }
    }
    return defaultValue
  })

  const setStoredValue = (val: T): void => {
    setValue(val)
    localStorage.setItem(key, JSON.stringify(val))
  }

  return [value, setStoredValue]
}

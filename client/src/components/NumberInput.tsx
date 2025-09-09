import { Input } from "@/components/ui/input"
import { useEffect, useState } from "react"

interface NumberInputProps {
  name: string
  value: number
  min?: number
  max?: number
  onChange: (name: string, value: number) => void
}

export default function NumberInput({
  name,
  value,
  min = -Infinity,
  max = Infinity,
  onChange,
}: NumberInputProps): JSX.Element {
  const [internal, setInternal] = useState(String(value))

  useEffect(() => {
    setInternal(String(value))
  }, [value])
  const clamp = (val: number): number => Math.max(min, Math.min(max, val))

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const val = e.target.value
    setInternal(val)
  }

  const handleBlur = (): void => {
    const parsed = Number(internal)
    const clamped = clamp(parsed)
    setInternal(String(clamped))
    onChange(name, clamped)
  }

  return (
    <Input
      name={name}
      value={internal}
      onChange={handleChange}
      onBlur={handleBlur}
      type="number"
      min={min}
      max={max}
    />
  )
}

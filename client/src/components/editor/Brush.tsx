import Field from "@/components/editor/Field"
import { EditorBrush, EditorBrushTypes } from "@/core/Brushes"
import { Scaffold } from "@/types"
import { useForceUpdate } from "@/utils/util"

export default function Brush({
  brush,
  scaffold,
}: {
  brush: EditorBrush
  scaffold: Scaffold
}): JSX.Element {
  const { config } = scaffold
  const forceUpdate = useForceUpdate()

  let combinedFields = { ...brush.fields }

  for (const [, field] of Object.entries(brush.fields)) {
    if (field.type === EditorBrushTypes.SINGLE_SELECT) {
      const selectedOption = field.options?.find((opt) => opt.value === field.value)
      if (selectedOption?.attributes?.fields) {
        combinedFields = {
          ...combinedFields,
          ...selectedOption.attributes.fields,
        }
      }
    }
  }

  if (config?.allowAgentTypes) {
    delete combinedFields.amount
  }

  const selectFields = Object.entries(combinedFields).filter(
    ([, field]) => field.type === EditorBrushTypes.SINGLE_SELECT
  )
  const otherFields = Object.entries(combinedFields).filter(
    ([, field]) => field.type !== EditorBrushTypes.SINGLE_SELECT
  )

  const handleChange = (): void => {
    forceUpdate()
  }

  return (
    <div className="flex flex-col">
      <div className="flex flex-col space-y-4">
        {selectFields.map(([key, field]) => (
          <div key={key}>
            <Field field={field} onChange={handleChange} />
          </div>
        ))}
      </div>

      <div
        className={`flex flex-row gap-2 flex-wrap ${selectFields.length === 0 ? "" : "mt-2"}`}
      >
        {otherFields.map(([key, field]) => (
          <div key={key} className="flex-1 min-w-[120px]">
            <Field field={field} onChange={handleChange} />
          </div>
        ))}
      </div>
    </div>
  )
}

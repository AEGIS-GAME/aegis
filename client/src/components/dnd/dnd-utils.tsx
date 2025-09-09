import { schema } from "aegis-schema"
import { Building2, Layers3, User } from "lucide-react"

export const getObjectId = (obj: schema.WorldObject): string => {
  if (obj.object.oneofKind === "survivor") {
    return `survivor-${obj.object.survivor.id}`
  } else if (obj.object.oneofKind === "rubble") {
    return `rubble-${obj.object.rubble.id}`
  }
  return "unknown"
}

export const getLayerIcon = (type: string): JSX.Element => {
  switch (type) {
    case "survivor":
      return <User className="w-4 h-4" />
    case "rubble":
      return <Building2 className="w-4 h-4" />
    default:
      return <Layers3 className="w-4 h-4" />
  }
}

export const getLayerColor = (type: string): string => {
  switch (type) {
    case "survivor":
      return "bg-green-100 text-green-800 border-green-200"
    case "rubble":
      return "bg-orange-100 text-orange-800 border-orange-200"
    default:
      return "bg-gray-100 text-gray-800 border-gray-200"
  }
}

import { schema } from "aegis-schema"
import Round from "./Round"
import World from "./World"

export enum EditorBrushTypes {
  POSITIVE_INTEGER,
  ZERO_OR_MORE,
  SINGLE_SELECT,
}

export type EditorFieldBase = {
  type: EditorBrushTypes
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  value: any
  label: string
  options?: EditorFieldOption[]
}

export type EditorField = EditorFieldBase & {
  type: EditorBrushTypes
}

export type EditorFieldOption = {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  value: any
  label: string
  attributes?: {
    fields: Record<string, EditorField>
  }
}

export abstract class EditorBrush {
  abstract readonly name: string
  abstract readonly fields: Record<string, EditorField>
  abstract apply(
    x: number,
    y: number,
    fields: Record<string, EditorField>,
    rightClick: boolean
  ): void
  public open: boolean = false

  constructor(public readonly world: World) {}

  withOpen(open: boolean): this {
    const clone = Object.create(Object.getPrototypeOf(this))
    Object.assign(clone, this, { open })
    return clone
  }
}

export class ZoneBrush extends EditorBrush {
  name = "Zone"

  public readonly fields: Record<string, EditorField> = {
    zoneType: {
      type: EditorBrushTypes.SINGLE_SELECT,
      value: schema.CellType.SPAWN,
      label: "Zone Type",
      options: [
        {
          value: schema.CellType.SPAWN,
          label: "Spawn",
          attributes: {
            fields: {
              amount: {
                type: EditorBrushTypes.ZERO_OR_MORE,
                label: "Spawn Amount",
                value: 0,
              },
            },
          },
        },
        { value: schema.CellType.KILLER, label: "Killer" },
        { value: schema.CellType.CHARGING, label: "Charging" },
      ],
    },
  }

  constructor(round: Round) {
    super(round.world)
  }

  apply(
    x: number,
    y: number,
    fields: Record<string, EditorField>,
    rightClick: boolean
  ): void {
    const cell = this.world.cellAt(x, y)
    if (!cell || cell.layers.length > 0) {
      return
    }

    const cellType = fields.zoneType.value as schema.CellType

    if (rightClick) {
      cell.type = schema.CellType.NORMAL

      if (cellType === schema.CellType.SPAWN) {
        this.world.initSpawns = this.world.initSpawns.filter(
          (spawn) => spawn.loc!.x !== x || spawn.loc!.y !== y
        )
      }
      return
    }

    cell.type = Number(cellType)

    if (cellType === schema.CellType.SPAWN) {
      const loc = schema.Location.create({ x, y })
      const amount = Number(
        fields.zoneType.options?.find((opt) => opt.value === cellType)?.attributes
          ?.fields.amount?.value ?? 0
      )

      // Remove previous entry for this location
      this.world.initSpawns = this.world.initSpawns.filter(
        (spawn) => spawn.loc!.x !== x || spawn.loc!.y !== y
      )

      // Add new spawn info
      this.world.initSpawns.push({
        loc,
        amount,
      })
    }
  }
}

export class LayersBrush extends EditorBrush {
  name = "Layers"
  private nextID: number = 0

  public readonly fields: Record<string, EditorField> = {
    objectType: {
      type: EditorBrushTypes.SINGLE_SELECT,
      label: "Layer Type",
      value: "survivor",
      options: [
        {
          label: "Survivor",
          value: "survivor",
          attributes: {
            fields: {
              survivor_hp: {
                type: EditorBrushTypes.POSITIVE_INTEGER,
                label: "Survivor HP",
                value: 1,
              },
            },
          },
        },
        {
          label: "Rubble",
          value: "rubble",
          attributes: {
            fields: {
              rubble_energyRequired: {
                type: EditorBrushTypes.POSITIVE_INTEGER,
                label: "Energy Required",
                value: 1,
              },
              rubble_agentsRequired: {
                type: EditorBrushTypes.POSITIVE_INTEGER,
                label: "Agents Required",
                value: 1,
              },
            },
          },
        },
      ],
    },
  }

  constructor(round: Round) {
    super(round.world)
  }

  apply(
    x: number,
    y: number,
    fields: Record<string, EditorField>,
    rightClick: boolean
  ): void {
    const cell = this.world.cellAt(x, y)
    if (!cell || cell.type !== schema.CellType.NORMAL) {
      return
    }

    if (rightClick) {
      // only pop the layer that is the same as the selected brush type (dont allow having the ruble brush selected and right clicking to pop a surv off)
      const type = fields.objectType.value
      const object = fields.objectType.options!.find((opt) => opt.value === type)!
      if (object.attributes!.fields.survivor_hp) {
        const survivor = cell.layers.find((l) => l.object.oneofKind === "survivor")
        if (survivor) {
          cell.layers.splice(cell.layers.indexOf(survivor), 1)
        }
      } else if (object.attributes!.fields.rubble_energyRequired) {
        const rubble = cell.layers.find((l) => l.object.oneofKind === "rubble")
        if (rubble) {
          cell.layers.splice(cell.layers.indexOf(rubble), 1)
        }
      }
      return
    }

    const type = fields.objectType.value
    const object = fields.objectType.options!.find((opt) => opt.value === type)!

    if (type === "survivor") {
      const attributes = object.attributes!.fields
      const hp = attributes.survivor_hp.value
      const survivor: schema.Survivor = schema.Survivor.create({
        id: this.nextID++,
        health: hp,
        state: schema.SurvivorState.ALIVE,
      })
      cell.layers.push({
        object: {
          oneofKind: "survivor",
          survivor,
        },
      })
    }

    if (type === "rubble") {
      const attributes = object.attributes!.fields
      const energyRequired = attributes.rubble_energyRequired.value
      const agentsRequired = attributes.rubble_agentsRequired.value
      const rubble: schema.Rubble = schema.Rubble.create({
        id: this.nextID++,
        energyRequired,
        agentsRequired,
      })
      cell.layers.push({
        object: {
          oneofKind: "rubble",
          rubble,
        },
      })
    }
  }
}

export class MoveCostBrush extends EditorBrush {
  name = "Move Cost"

  public readonly fields: Record<string, EditorField> = {
    moveCost: {
      type: EditorBrushTypes.POSITIVE_INTEGER,
      value: 1,
      label: "Move Cost",
    },
  }

  constructor(round: Round) {
    super(round.world)
  }

  apply(
    x: number,
    y: number,
    fields: Record<string, EditorField>,
    rightClick: boolean
  ): void {
    const cell = this.world.cellAt(x, y)
    if (!cell || cell.type !== schema.CellType.NORMAL) {
      return
    }

    const moveCost = fields.moveCost.value

    if (cell.type !== schema.CellType.NORMAL) {
      return
    }

    if (rightClick) {
      cell.moveCost = 1
    } else {
      cell.moveCost = moveCost
    }
  }
}

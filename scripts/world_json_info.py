import json
import argparse


def summarize_world(world_json):
    world = json.loads(world_json)

    # World info
    size = world["settings"]["world_info"]["size"]
    seed = world["settings"]["world_info"]["seed"]
    energy = world["settings"]["world_info"]["agent_energy"]
    print(f"World Size: {size['width']} x {size['height']}")
    print(f"Seed: {seed}")
    print(f"Agent Energy: {energy}\n")

    # Spawn locations (sorted)
    print("Spawn Locations:")
    for spawn in sorted(world["spawn_locs"], key=lambda s: (s["x"], s["y"])):
        print(f"  - ({spawn['x']}, {spawn['y']}) type: {spawn['type']}")
    print()

    # Killer cells (sorted)
    print("Killer Cells:")
    for kc in sorted(
        world["cell_types"].get("killer_cells", []), key=lambda c: (c["x"], c["y"])
    ):
        print(f"  - ({kc['x']}, {kc['y']})")
    print()

    # Charging cells (sorted)
    print("Charging Cells:")
    for cc in sorted(
        world["cell_types"].get("charging_cells", []), key=lambda c: (c["x"], c["y"])
    ):
        print(f"  - ({cc['x']}, {cc['y']})")
    print()

    # Stacks (sorted)
    print("Stacks with move_cost > 1 or contents:")
    for stack in sorted(
        world["stacks"], key=lambda s: (s["cell_loc"]["x"], s["cell_loc"]["y"])
    ):
        x, y = stack["cell_loc"]["x"], stack["cell_loc"]["y"]
        move_cost = stack["move_cost"]
        contents = stack.get("contents", [])
        if move_cost > 1 or contents:
            content_desc = (
                ", ".join([f"{c['type']}({c.get('arguments', {})})" for c in contents])
                or "none"
            )
            print(f"  - ({x},{y}) move_cost: {move_cost} contents: {content_desc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize a world JSON file.")
    parser.add_argument("file", type=str, help="Path to the world JSON file")
    args = parser.parse_args()

    with open(args.file, "r") as f:
        world_json = f.read()

    summarize_world(world_json)

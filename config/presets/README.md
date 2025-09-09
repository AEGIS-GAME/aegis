# Configuration Presets

These preset files contain example configurations that you can copy into the main `config/config.yaml` file. They are packaged into aegis release for use with `aegis init` which starts off config.yml based on one of these presets

## How to use presets:

1. Choose a preset file that matches your needs
2. Copy the relevant settings from the preset file
3. Paste those settings into `config/config.yaml`
4. Modify the settings in `config/config.yaml` as needed

## Available Presets:

- `pathfinding-assignment.yaml` - Settings for pathfinding assignment
- `multi-agent-assignment.yaml` - Settings for multi-agent assignment
- `competition.yaml` - Configuration for competition mode with two teams

## Example:

If you want to use the pathfinding preset:

1. Open `pathfinding-assignment.yaml` and copy the settings
2. Open `config/config.yaml`
3. Replace the relevant sections with the copied settings
4. Save `config/config.yaml`

**Remember: Only `config/config.yaml` is read by the AEGIS system. These preset files are just templates!**

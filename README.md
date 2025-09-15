## AEGIS

AEGIS is a survivor simulation game. This repo contains:

- Server/engine (Python package) that runs simulations and exposes a WebSocket for the client
- Client (Electron, React, TypeScript, Tailwind CSS) for visualizing and controlling simulations
- Documentation found [here](https://aegis-game.github.io/docs/)

### Repo Layout

Codebase
- `client`: Electron desktop client (builds for macOS, Windows, Linux)
- `schema`: Shared Protocol Buffer/TypeScript types
- `src`: Python server/engine, CLI entrypoint, public API
- `tests`: Tests

Additional
- `agents`: Example/reference agents (e.g., `agent_path`, `agent_mas`, `agent_prediction`)
- `config`: Example/reference configurations (e.g., `pathfinding-assignment.yaml`, `multi-agent-assignment.yaml`)
- `prediction-data`:  Example/reference prediction data
- `scripts`: Utility scripts
- `worlds`: Example/reference worlds for running simulations

### Prerequisites

- Python 3.13+
- Node.js 20+
  
### Package name (PyPI)

The Python package is published as `aegis-game`. You can install it with:

```bash
pip install aegis-game
```
- If you see "Defaulting to user installation because normal site-packages is not writeable"
  - You will likely get "aegis: command not found" (Linux)  or "'aegis' is not recognized as an internal or external command, operable program or batch file." (Windows) when using it
  - This can be rectfied by adding the local location of 'aegis' to your PATH
    - Linux 
      - `PATH=$PATH:~/.local/bin`
    - Windows
      - `PATH=%PATH%;%appdata%\Python\Python313\Scripts`

The CLI entrypoint is `aegis` (e.g., `aegis launch`).

### Download for usage in assignments or competitions

1. Create a folder and install the `aegis-game` package 

```bash
# Initialize project
mkdir my-new-project
cd my-new-project
aegis init
```

Alternately, for multi-agent config use
  ```bash
  aegis init --type mas
  ```
  
This creates all necessary files/folders in your project that an aegis simulation needs to run

Notes:

- Agent code under `agents/`
- Config code under `config/`
- Client GUI code under `client/`
- Worlds under `worlds/` 

2. Configure features (Optional)

If default `aegis init` is not desired edit `config/config.yaml` to enable/disable features (e.g., messages, dynamic spawning, abilities). If you change features, regenerate stubs so the API your agent recongizes matches the config:

```bash
aegis forge
```

3a. Use the client UI

The client is in the `\client` folder
You can run it by interacting with it through your OS folder system or

Linux
```bash
cd client
./aegis-client.AppImage
```
Windows
```cmd
cd client
aegis-client.exe
```
Mac
```console
cd client
open Aegis.app
```

3b. Launch a game (through the console)

```bash
# One agent
aegis launch --world example --agent agent_path

# Five agents with max rounds of 500 (requires config of ALLOW_CUSTOM_AGENT_COUNT=true)
aegis launch --world example --agent agent_path --amount 5 --rounds 500

```

Run `aegis launch -h` to see all ways you can run an aegis simulation

### Download for Development

Before you start, please read our [Contributing Guidelines](https://github.com/AEGIS-GAME/aegis/blob/main/CONTRIBUTING.md) to understand
the full contribution process, coding standards, and PR requirements.

1. Clone the repository and set up the Python environment
   
 - `uv` (optional for dev) — `pip install uv` or see `https://docs.astral.sh/uv/`
   - If you see "Defaulting to user installation because normal site-packages is not writeable"
     - You will likely get "uv: command not found"  or "'uv' is not recognized as an internal or external command, operable program or batch file." when using it, this can be rectfied by adding the local location of 'uv' to your PATH
     - Linux (eg.)
       - `PATH=$PATH:~/.local/bin`
     - Windows (eg.)
       - `PATH=%PATH%;%appdata%\Python\Python313\Scripts`

```bash
git clone https://github.com/AEGIS-GAME/aegis.git
cd aegis
uv sync --group dev
```

2. Activate the virtual environment

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Run locally

```bash
aegis launch --world ExampleWorld --agent agent_path
```

### Client

For instructions on local development and setup of the client application, please see the [client README](https://github.com/AEGIS-GAME/aegis/blob/main/client/README.md)

### Documentation

The documentation can be found [here](https://github.com/AEGIS-GAME/aegis-docs).

### Troubleshooting

- "Config Error Failed to load config.yaml. Please check your config file and ensure it's valid."
  - Use Settings 'Gear' icon to open settings and set 'Aegis Path' to the base folder of your project
      - The folder 'config' within that base folder should have the missing 'config.yaml' in it
- Windows PowerShell execution policy may block script activation; if needed, run PowerShell as Administrator and execute:
  - `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
- Ensure Node.js 20+ and Python 3.13+ are on your PATH
- If the client cannot connect, verify the server was started with `--client` and that no firewall is blocking the port

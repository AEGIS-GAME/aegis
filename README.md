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

- The Python package is published as `aegis-game`. 

### Download for usage in assignments or competitions

0. Verify Python version accessible from shell (Should be 3.13+)

```bash
python --version
# OR if you have Python 2 installed (often the case on Mac/Linux)
python3 --version
```

1. Create a folder and install the `aegis-game` package 

```bash
# Initialize project
mkdir my-new-project
cd my-new-project
```

2. Activate the virtual environment

```bash
python -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows (CMD):

```cmd
.\.venv\Scripts\Activate
```

On Windows (PowerShell):

```cmd
.\.venv\Scripts\Activate.ps1
```

This creates a virtual project environment under `.venv/`

3. Install `aegis-game` with:

```bash
pip install aegis-game
```

The CLI entrypoint is `aegis` (e.g., `aegis launch`).

### Download for usage in assignments or competitions

3. Create folder scaffold

```bash
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

4. Configure features (Optional)

If default `aegis init` is not desired edit `config/config.yaml` to enable/disable features (e.g., messages, dynamic spawning, abilities). If you change features, regenerate stubs so the API your agent recongizes matches the config:

```bash
aegis forge
```

5a. Use the client UI

The client is in the `\client` folder
You can run it by interacting with it through your OS folder system or

On Linux
```bash
client/aegis-client.AppImage
```

On Windows (CMD/PowerShell):
```cmd
client\aegis-client.exe
```

On Mac:
```console
open client/Aegis.app
```

5b. Launch a game (through the console)

```bash
# One agent
aegis launch --world example --agent agent_path

# Five agents with max rounds of 500 (requires config of ALLOW_CUSTOM_AGENT_COUNT=true)
aegis launch --world example --agent agent_path --amount 5 --rounds 500

```

Run `aegis launch -h` to see all ways you can run an aegis simulation

6. Deactivate (venv)
Close your terminal/shell or run command

```bash
deactivate
```

&. Reactivate (venv)
Open terminal shell within project folder or change directory into it and run

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows (CMD):

```cmd
.\.venv\Scripts\Activate
```

On Windows (PowerShell):

```cmd
.\.venv\Scripts\Activate.ps1
```


### Download for Development

Before you start, please read our [Contributing Guidelines](https://github.com/AEGIS-GAME/aegis/blob/main/CONTRIBUTING.md) to understand
the full contribution process, coding standards, and PR requirements.

1. Clone the repository and set up the Python environment

- `uv` (for Python env/build) — `pip install uv` or see `https://docs.astral.sh/uv/`

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

On Windows (CMD):

```cmd
.\.venv\Scripts\Activate
```

On Windows (PowerShell):

```cmd
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
- If you aren't using a virtual environment (.venv) and see "Defaulting to user installation because normal site-packages is not writeable" during pip 
  - You will likely get "<package>: command not found" (Linux)  or "'<package>' is not recognized as an internal or external command, operable program or batch file." (Windows) when using commands
  - This can be rectfied by adding the local location of '<package>' to your PATH. A local installation for python package installed via pip is generally able to be added to path with
    - Linux 
      - ```bash
        PATH=$PATH:~/.local/bin```
    - Windows
      - ```cmd
        PATH=%PATH%;%appdata%\Python\Python313\Scripts```

## AEGIS

AEGIS is a survivor simulation game. This repo contains:

- Server/engine (Python package) that runs simulations and exposes a WebSocket for the client
- Client (Electron, React, TypeScript, Tailwind CSS) for visualizing and controlling simulations
- Documentation site (Next.js/MDX)

### Repo Layout

- `src/_aegis` and `src/aegis`: Python engine, CLI entrypoint, public API
- `client`: Electron desktop client (builds for macOS, Windows, Linux)
- `docs`: Documentation website and content
- `schema`: Shared Protocol Buffer/TypeScript types
- `worlds`: Sample worlds for running simulations
- `agents`: Example/reference agents (e.g., `agent_path`, `agent_mas`, `agent_prediction`)
- `config/config.yaml`: Runtime configuration for the engine

### Prerequisites

- Python 3.12+
- Node.js 20+
- `uv` (for Python env/build) — `pip install uv` or see `https://docs.astral.sh/uv/`

### Package name (PyPI)

The Python package is published as `aegis-game`. Once released, you can install it with:

```bash
pip install aegis-game
```

The CLI entrypoint is `aegis` (e.g., `aegis launch`).

### Download for usage in assignments or competitions

1. Create a python project and install the `aegis-game` package (Any method works, will demo with uv)

```bash
# Initialize project
uv init --package my-new-project
cd my-new-project

# Add the aegis-game package as a dependency
uv add aegis-game
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

3. Create scaffold

```
aegis init
```

This creates all necessary files/folders in your project that an aegis simulation needs to run

4. Configure features

Edit `config/config.yaml` to enable/disable features (e.g., messages, dynamic spawning, abilities). If you change features, regenerate stubs so the API your agent recongizes matches the config:

```bash
aegis forge
```

5. Launch a game (through the console)

```bash
# One agent
aegis launch --world ExampleWorld --agent agent_path

# Five agents with max rounds of 500 (requires config of ALLOW_CUSTOM_AGENT_COUNT=true)
aegis launch --world ExampleWorld --agent agent_path --amount 5 --rounds 500

```

Run `aegis launch -h` to see all ways you can run an aegis simulation

Notes:

- World names are the file names under `worlds/` without the `.world` extension. For example, `worlds/ExampleWorld.world` -> `--world ExampleWorld`.
- Agent names are folder names under `agents/`. For example, `agents/agent_path` -> `--agent agent_path`.

6. Use the client UI

TODO

### Download for Development

Before you start, please read our [Contributing Guidelines](https://github.com/AEGIS-GAME/aegis/blob/main/CONTRIBUTING.md) to understand
the full contribution process, coding standards, and PR requirements.

1. Clone the repository and set up the Python environment

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

- Windows PowerShell execution policy may block script activation; if needed, run PowerShell as Administrator and execute:
  - `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
- Ensure Node.js 20+ and Python 3.12+ are on your PATH
- If the client cannot connect, verify the server was started with `--client` and that no firewall is blocking the port

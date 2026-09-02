# Aegis Schema

Protobuf schemas for Aegis.

## Prerequisites

You need `protoc` version **36.x**.  
This corresponds to Protobuf Python runtime v6. Refer to the official version support chart to match the correct `protoc` version if needed:
https://protobuf.dev/support/version-support/

**Important**: The generated protobuf files require protobuf Python runtime >= 7.36.1. Make sure your project dependencies include `protobuf>=7.36.1`.

## How to Use

1. Activate the virtual environment (from the project root):

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows (CMD):

```batch
.\.venv\Scripts\Activate
```

On Windows (PowerShell) [see Troubleshooting below if activation gets blocked]:

```pwsh
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
npm install
```

3. Build the schema:

```bash
npm run build
```

This will generate the protobuf files for both Python and TypeScript and install (copy) them into their respective directories.

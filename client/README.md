# Aegis Client

## Local Development

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

3. Start the development server:

```bash
npm run dev
```

## Building

Build the Client:

```bash
npm run build
```

If you get an error similar to the following for "aegis/schema/ts/*.ts" during build,

```bash
error during build:
[vite]: Rollup failed to resolve import "@protobuf-ts/runtime" from ".../aegis/schema/ts/cell.ts".
```

Then proceed to build the schema first. Although build schema files are distributed already

For instructions on schema, please see the [schema README](https://github.com/AEGIS-GAME/aegis/blob/main/schema/README.md) and then return here to build the client.

## Packing

Pack the Client:

```bash
npm run build:pack
```

You may experience packing issues due to adminstrator rights on Windows. For one example, the Windows Code Sign compressed file downloaded by electron-builder has a symbolic link in it and 7Zip command fails extraction due to lacking administrator rights like the following.

```bash
                    errorOut=ERROR: Cannot create symbolic link : A required privilege is not held by the client. : C:\Users\jonat\AppData\Local\electron-builder\Cache\winCodeSign\568883111\darwin\10.12\lib\libcrypto.dylib
    ERROR: Cannot create symbolic link : A required privilege is not held by the client. : C:\Users\jonat\AppData\Local\electron-builder\Cache\winCodeSign\568883111\darwin\10.12\lib\libssl.dylib
    
                    command='D:\aegis\aegis\client\node_modules\7zip-bin\win\x64\7za.exe' x -bd 'C:\Users\jonat\AppData\Local\electron-builder\Cache\winCodeSign\568883111.7z' '-oC:\Users\jonat\AppData\Local\electron-builder\Cache\winCodeSign\568883111'
                    workingDir=C:\Users\jonat\AppData\Local\electron-builder\Cache\winCodeSign
  • Above command failed, retrying 1 more times
```

There are suggestions that running VSCode in adminstrator mode, or turning off requirement for signed scripts in System->Advanced->PowerShell can solve this, but the below option of performing file download and extraction yourself is safer step as it solves only the problem without open security attack surface area.

[Solution](https://github.com/electron-userland/electron-builder/issues/8149#issuecomment-4790246052)

## Using client

It is recommended to not use client in development directory as the folder structure of config/agents/worlds/etc. and the source aegis_game are not in the locations/structure expected by the client. Instead, follow regular deployment steps and then copy client (and/or) modified aegis_game files over that directory for local development.

## Deployment

Check the main readme to see how to deploy.

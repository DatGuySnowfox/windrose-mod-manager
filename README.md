# Windrose Mod Deployer

A Windows desktop application for managing mods for **Windrose** — supporting both the client game and the dedicated server.

## What It Does

- **Detects** Windrose client, dedicated server, and local config/save paths automatically
- **Analyzes** mod archives (.zip, .7z, .rar) before install — classifies as pak-only, loose-file, mixed, or multi-variant
- **Deploys** mods to client, server, or both with proper file placement
- **Drag-and-drop** archive import (requires `tkinterdnd2`)
- **Backs up** every file before overwriting and maintains a full backup history
- **Tracks** all installed files in a manifest so mods can be cleanly uninstalled or disabled
- **Edits** `ServerDescription.json` safely with validation and automatic backups
- **Edits** `WorldDescription.json` — multipliers, presets, combat difficulty, and boolean settings
- **Detects conflicts** between installed mods writing to the same target files
- **Provides** a clean dark-mode desktop UI built with CustomTkinter

## Feature Status

| Feature | Status |
|---|---|
| Client/server path detection | Done |
| Archive analysis (.zip, .7z, .rar) | Done |
| Drag-and-drop archive import | Done |
| Pak-only mod install | Done |
| Loose-file mod install | Done |
| Mixed mod install | Done |
| Multi-variant pak selection | Done |
| Install to client/server/both | Done |
| Manifest-tracked uninstall | Done |
| Mod disable/enable | Done |
| Backup & restore | Done |
| ServerDescription.json editor | Done |
| WorldDescription.json editor | Done |
| Conflict warnings | Done |
| Path traversal protection | Done |
| Test suite | Done |

## Project Structure

```
windrose-mod-deployer/
  app.py                          # Entry point (with crash dialog)
  requirements.txt
  README.md
  windrose_deployer/
    __init__.py
    models/                       # Data classes
      app_paths.py                # Path configuration model
      archive_info.py             # Archive analysis result
      deployment_record.py        # Deployment tracking record
      mod_install.py              # Installed mod state
      server_config.py            # ServerDescription model
      world_config.py             # WorldDescription model
    core/                         # Business logic
      archive_handler.py          # Unified archive reader (.zip/.7z/.rar)
      archive_inspector.py        # Archive content analysis
      backup_manager.py           # Backup/restore operations
      conflict_detector.py        # File conflict detection
      deployment_planner.py       # Plan install operations
      discovery.py                # Auto-detect game paths
      installer.py                # Execute installs/uninstalls
      logging_service.py          # App-wide logging
      manifest_store.py           # Persistent mod manifest
      server_config_service.py    # ServerDescription.json I/O
      target_resolver.py          # Resolve install targets
      validators.py               # Path/config validation
      world_config_service.py     # WorldDescription.json I/O
    ui/                           # CustomTkinter UI
      app_window.py               # Main window
      widgets/
        status_panel.py           # Status/log panel
        file_preview.py           # Archive file tree preview
      tabs/
        mods_tab.py               # Add & install mods
        installed_tab.py          # Manage installed mods
        server_tab.py             # Server + world config editor
        backups_tab.py            # Backup history & restore
        settings_tab.py           # Path configuration
    utils/                        # Shared helpers
      filesystem.py               # Safe file operations
      hashing.py                  # File hashing
      json_io.py                  # JSON read/write helpers
      naming.py                   # Name/path utilities
  tests/                          # Test suite (pytest)
  data/                           # Manifest & app state (auto-created)
  backups/                        # Backup storage (auto-created)
```

## How to Run

### Prerequisites

- Python 3.12+
- Windows 10/11

### Setup

```bash
cd "H:\Moddding\Windrose\Windrose Mod Deployer"

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

### Run Tests

```bash
python -m pytest tests/ -v
```

## Supported Mod Types

| Type | Description |
|---|---|
| **Pak-only** | Archives containing `.pak` files (optionally with `.utoc`/`.ucas`) |
| **Loose-file** | Archives with folder structures to overlay onto the game directory |
| **Mixed** | Archives containing both pak files and loose files |
| **Multi-variant** | Archives with multiple alternative pak files — user selects which to install |

## Supported Archive Formats

| Format | Notes |
|---|---|
| `.zip` | Full support |
| `.7z` | Requires `py7zr` (included in requirements) |
| `.rar` | Requires `rarfile` + UnRAR executable on PATH |

**RAR note:** The `rarfile` Python package requires the [UnRAR](https://www.rarlab.com/rar_add.htm) command-line tool to be installed and available on your system PATH. Without it, `.rar` archives will fail to open.

## Where Data Lives

| Data | Location (source mode) | Location (packaged exe) |
|---|---|---|
| App state / manifest | `./data/app_state.json` | `%LOCALAPPDATA%/WindroseModDeployer/data/` |
| Settings | `./data/settings.json` | `%LOCALAPPDATA%/WindroseModDeployer/data/` |
| Backups | `./backups/` | `%LOCALAPPDATA%/WindroseModDeployer/backups/` |
| Logs | `./data/windrose_deployer.log` | `%LOCALAPPDATA%/WindroseModDeployer/data/` |

## Known Limitations

- No automatic mod updates or version tracking
- Conflict detection is warning-only — no load-order management
- Discovery scans common Steam library drive letters (C–H); non-standard Steam library locations require manual browse
- `os.startfile` used for "open folder" buttons — Windows-only
- No networked features (no Nexus API, no auto-downloads)
- No save editing
- No UE asset unpacking or pak creation

## Packaging Notes

The app is designed to be packaged with PyInstaller:

- Entry point: `app.py` with global crash dialog
- When frozen (`sys.frozen`), data/backups write to `%LOCALAPPDATA%/WindroseModDeployer/`
- Optional dependencies (`tkinterdnd2`, `py7zr`, `rarfile`) degrade gracefully if missing
- No fragile relative imports — all imports go through the `windrose_deployer` package

Example PyInstaller command (untested):
```bash
pyinstaller --onedir --windowed --name "Windrose Mod Deployer" app.py
```

## Future Roadmap

- Mod profiles (save/load sets of enabled mods)
- PyInstaller packaging for standalone `.exe`
- Mod version tracking and update detection
- Search/filter in installed mods list
- Startup health check summary

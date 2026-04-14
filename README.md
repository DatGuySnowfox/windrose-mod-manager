# Windrose Mod Manager

A Windows desktop application for managing mods for **Windrose**, supporting both the client game and the dedicated server.

**[Nexus Mods Page](https://www.nexusmods.com/windrose/mods/29)** | **[GitHub](https://github.com/Vercadi/windrose-mod-manager)**

## Features

- Auto-detects Windrose client, dedicated server, and local config/save paths
- Analyzes mod archives (.zip, .7z, .rar) before install, classifying as pak-only, loose-file, mixed, or multi-variant
- Persistent **Archive Library** that remembers your mod archives with install status indicators
- Deploys mods to client, server, or both with proper file placement
- **Variant detection** for archives with multiple pak options (e.g. stack size multipliers), forcing you to pick one
- **Quick install** via double-click or right-click on library entries
- **Install All** button to batch-install non-installed archives
- **Uninstall**, **Reinstall**, and **Uninstall All** for easy mod management
- Drag-and-drop archive import (single or multiple files)
- Backs up every file before overwriting and maintains a full backup history
- Tracks all installed files in a manifest for clean uninstall or disable/enable
- Edits `ServerDescription.json` and `WorldDescription.json` safely with validation and automatic backups
- Detects conflicts between installed mods writing to the same target files
- **Start Game** and **Start Server** buttons on all tabs
- **Search/filter** in the Installed tab
- **Update notifications** via GitHub Releases (automatic on startup + manual check in About tab)
- Installed mod count badge
- Clean dark-mode UI built with CustomTkinter

## Download

Grab the latest release from [Nexus Mods](https://www.nexusmods.com/windrose/mods/29) or [GitHub Releases](https://github.com/Vercadi/windrose-mod-manager/releases).

## Running from Source

### Prerequisites

- Python 3.12+
- Windows 10/11

### Setup

```bash
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
| **Multi-variant** | Archives with multiple alternative pak files. User selects which to install |

## Supported Archive Formats

| Format | Notes |
|---|---|
| `.zip` | Full support |
| `.7z` | Requires `py7zr` (included in requirements) |
| `.rar` | Requires `rarfile` + UnRAR executable on PATH |

**RAR note:** The `rarfile` Python package requires the [UnRAR](https://www.rarlab.com/rar_add.htm) command-line tool to be installed and available on your system PATH. Without it, `.rar` archives will fail to open.

## Project Structure

```
windrose-mod-manager/
  app.py                          # Entry point
  requirements.txt
  windrose_deployer/
    __init__.py                   # Version and app name
    models/                       # Data classes
      app_paths.py
      archive_info.py
      deployment_record.py
      mod_install.py
      server_config.py
      world_config.py
    core/                         # Business logic
      archive_handler.py          # Unified archive reader (.zip/.7z/.rar)
      archive_inspector.py        # Archive content analysis and variant detection
      backup_manager.py
      conflict_detector.py
      deployment_planner.py
      discovery.py                # Auto-detect game paths
      installer.py
      logging_service.py
      manifest_store.py
      server_config_service.py
      target_resolver.py
      update_checker.py           # GitHub Releases update check
      validators.py
      world_config_service.py
    ui/
      app_window.py               # Main window, launch bar, update banner
      widgets/
        status_panel.py
      tabs/
        mods_tab.py               # Archive library, inspect, install
        installed_tab.py          # Manage installed mods
        server_tab.py             # Server + world config editor
        backups_tab.py            # Backup history and restore
        settings_tab.py           # Path configuration
        about_tab.py              # App info, links, update check
    utils/
      filesystem.py
      hashing.py
      json_io.py
      naming.py
  tests/                          # Test suite (pytest)
  assets/                         # App icon files
  data/                           # Manifest and app state (auto-created)
  backups/                        # Backup storage (auto-created)
```

## Where Data Lives

| Data | Location (source mode) | Location (packaged exe) |
|---|---|---|
| App state / manifest | `./data/app_state.json` | `%LOCALAPPDATA%/WindroseModDeployer/data/` |
| Settings | `./data/settings.json` | `%LOCALAPPDATA%/WindroseModDeployer/data/` |
| Archive library | `./data/archive_library.json` | `%LOCALAPPDATA%/WindroseModDeployer/data/` |
| Backups | `./backups/` | `%LOCALAPPDATA%/WindroseModDeployer/backups/` |
| Logs | `./data/windrose_deployer.log` | `%LOCALAPPDATA%/WindroseModDeployer/data/` |

## Building the Executable

```bash
python -m PyInstaller windrose_mod_deployer.spec --noconfirm
```

The output lands in `dist/Windrose Mod Manager/`.

When packaged, the app writes data to `%LOCALAPPDATA%/WindroseModDeployer/` instead of the repo directory.

## Known Limitations

- No automatic mod updates or version tracking per mod
- Conflict detection is warning-only, no load-order management
- Discovery scans common Steam library drive letters (C-H); non-standard locations require manual browse
- Windows-only (uses `os.startfile` and Windows path conventions)
- No networked features beyond update checks (no Nexus API, no auto-downloads)
- No save editing, UE asset unpacking, or pak creation

## License

MIT License. See [LICENSE](LICENSE) for details.

## Author

**Vercadi**

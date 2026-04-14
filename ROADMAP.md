# Windrose Mod Manager - Roadmap

## v0.2.0 - Trust Baseline (current)

The first public build people will keep using. Safety invariants and identity must be correct before persistent user data exists in the wild.

### Safety & Identity
- [x] Uninstall restores originals from backup (not just delete)
- [x] Reinstall preflight validation (don't destroy working install before confirming replacement)
- [x] Accurate Install All counting (succeeded/failed/skipped)
- [x] UUID-based mod identity (no name collisions, stable across renames)
- [x] Manifest schema versioning with forward migration (v1 name-based ids auto-migrate to v2 UUIDs)
- [x] Pre-migration manifest backup (`app_state.v1.bak.json` created before any schema rewrite)
- [x] Manifest collision guard (safety net even with UUIDs)

### Safety Regression Tests
- [x] Overwrite install then uninstall restores original file content
- [x] Duplicate display names get different mod IDs
- [x] v1 manifests migrate to UUID-based v2 schema
- [x] Migration creates backup copy of old manifest before rewriting
- [x] Invalid plans report as failures, not successes

### Features
- [x] Archive library (persistent sidebar, survives restarts)
- [x] Quick install (double-click or right-click)
- [x] Uninstall from Mods tab (right-click or detail panel)
- [x] Installed mod count badge
- [x] Multi-mod drag/drop and browse
- [x] Start Game / Start Server buttons with combined launcher
- [x] About tab with version, author, links
- [x] Update check (GitHub Releases API, startup + manual)
- [x] Uninstall All button with confirmation
- [x] Installed tab search/filter
- [x] Reinstall option (with preflight)

### Release Gates
- [ ] `pytest` green (all safety + unit tests pass)
- [ ] Migration tested on a real pre-v0.2.0 `app_state.json` with name-based mod IDs
- [ ] Packaged-build smoke test: install, uninstall, reinstall cycle works correctly from the PyInstaller `.exe` (path behavior often changes once packaged)

---

## v0.2.1 - Polish & Confidence

Small fixes and UX improvements based on early user feedback.

- [ ] Grouped conflict display (by mod, file count, target path)
- [ ] Conservative variant detection (flag uncertain cases for user decision instead of guessing)
- [ ] Migration cleanup (remove any leftover v1 artifacts if needed)
- [ ] Better error messages for common failure modes
- [ ] UI polish based on first user reports

---

## v0.3.0 - Real Manager

The pivot from "installer UI" to a tool that can explain and recover its own changes.

### Core
- [ ] Verify install (check manifest against actual files on disk, report drift)
- [ ] Repair install (re-extract missing files from archive if archive is still available)
- [ ] Undo last install: requires an authoritative operation journal that tracks overwrites, restores, and partial failures, not just "remove the last mod." The journal must be the source of truth for reversal, covering the full range of what install/uninstall/reinstall can do.
- [ ] Health/status dashboard (missing archives, missing files, stale backups, broken paths)

### UX
- [ ] Archive metadata (user notes, category tags, Nexus URL/version)
- [ ] Better batch action summaries (succeeded/failed/skipped with reasons)
- [ ] Drift detection on startup (warn if files changed outside the manager)

---

## v0.4.0 - Server Differentiation

This is where the product becomes more useful than generic mod managers for Windrose server operators.

### Server-safe apply
- [ ] Apply workflow: validate mod set, deploy, prompt for server restart, verify post-restart
- [ ] Running-server detection and warning before writes
- [ ] Apply guidance: surface which changes need a server restart vs. which are hot-loadable (if any)

### Client/server sync validation
- [ ] Define source of truth: manifest is authoritative, on-disk scan is verification
- [ ] Detect mismatched mod states between client and server targets
- [ ] Surface sync status clearly (which mods are client-only, server-only, or both)

### WorldDescription.json workflows
- [ ] Per-world discovery (enumerate worlds under SaveProfiles, show active world from ServerDescription.json)
- [ ] Running-server save guard (warn and block if server process is detected)
- [ ] Backup diff/restore (show what changed between backups, restore specific versions)
- [ ] Apply guidance (which settings need world restart vs. server restart)

---

## v0.5.0 - Profiles

- [ ] Mod profiles (named sets of mods that can be switched)
- [ ] Per-world mod configurations
- [ ] Profile import/export

---

## v1.0 - Framework Extraction (future)

**Rule: don't build a framework until there is a second game. But keep the current code ready for extraction.**

Second adapter must prove the abstraction without changing Windrose behavior. The extraction is only valid if the Windrose adapter works identically before and after.

Current design seams to maintain:
- Windrose-specific discovery/config logic is grouped (not scattered)
- Path assumptions stay out of generic install/manifest/backup code
- Archive/install/manifest/backup logic is game-agnostic
- Plugin-style adapter model is the extraction target, not the current implementation

When a second UE game needs mod management, extract the generic core into a shared framework and keep Windrose as the first adapter.

---

## Design Principles

1. **The app should always be able to answer**: "what changed, what was replaced, and how do I get back to the previous state?"
2. **Don't ship persistent public state with weak identity semantics.** Fix identity before the first real release, not after.
3. **Design for extraction, don't perform extraction yet.** Light seams now, full plugin architecture later.
4. **Safety over features.** Every release must pass its safety regression suite.

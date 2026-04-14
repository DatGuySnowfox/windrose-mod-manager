"""Windrose Mod Deployer — entry point."""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def _enable_dpi_awareness() -> None:
    """Tell Windows this process is DPI-aware so it renders at native
    resolution instead of applying a blurry bitmap upscale."""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main() -> None:
    _enable_dpi_awareness()

    from windrose_deployer.ui.app_window import AppWindow
    app = AppWindow()
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        msg = traceback.format_exc()
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Windrose Mod Deployer — Fatal Error", msg)
            root.destroy()
        except Exception:
            print(msg, file=sys.stderr)
        sys.exit(1)

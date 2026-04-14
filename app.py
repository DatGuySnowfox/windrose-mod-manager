"""Windrose Mod Deployer — entry point."""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def main() -> None:
    from windrose_deployer.ui.app_window import AppWindow
    app = AppWindow()
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Show a crash dialog so packaged-exe users see the error
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

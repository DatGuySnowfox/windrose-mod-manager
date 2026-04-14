"""About tab — app info, author, and links."""
from __future__ import annotations

import webbrowser
from typing import TYPE_CHECKING

import customtkinter as ctk

from ... import __app_name__, __version__

if TYPE_CHECKING:
    from ..app_window import AppWindow

NEXUS_URL = "https://www.nexusmods.com/windrose/mods/29"
GITHUB_URL = "https://github.com/Vercadi/windrose-mod-manager"


class AboutTab(ctk.CTkFrame):
    def __init__(self, master, app: "AppWindow", **kwargs):
        super().__init__(master, **kwargs)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.4, anchor="center")

        ctk.CTkLabel(
            container,
            text=__app_name__,
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            container,
            text=f"Version {__version__}",
            font=ctk.CTkFont(size=16),
            text_color="#aaaaaa",
        ).pack(pady=(0, 12))

        ctk.CTkLabel(
            container,
            text="by Vercadi",
            font=ctk.CTkFont(size=14),
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            container,
            text="MIT License",
            font=ctk.CTkFont(size=12),
            text_color="#95a5a6",
        ).pack(pady=(0, 20))

        links = ctk.CTkFrame(container, fg_color="transparent")
        links.pack(pady=(0, 20))

        ctk.CTkButton(
            links, text="Nexus Mods Page", width=160,
            fg_color="#d98f40", hover_color="#b87530",
            command=lambda: webbrowser.open(NEXUS_URL),
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            links, text="GitHub Repository", width=160,
            fg_color="#555555", hover_color="#666666",
            command=lambda: webbrowser.open(GITHUB_URL),
        ).pack(side="left", padx=8)

        ctk.CTkLabel(
            container,
            text=(
                "A mod manager for Windrose — install, manage, and back up\n"
                "mods for the client game and dedicated server."
            ),
            font=ctk.CTkFont(size=12),
            text_color="#888888",
            justify="center",
        ).pack(pady=(0, 20))

        update_row = ctk.CTkFrame(container, fg_color="transparent")
        update_row.pack(pady=(0, 0))

        self._update_btn = ctk.CTkButton(
            update_row, text="Check for Updates", width=160,
            fg_color="#2980b9", hover_color="#2471a3",
            command=self._on_check_update,
        )
        self._update_btn.pack(side="left", padx=4)

        self._update_status = ctk.CTkLabel(
            update_row, text="", font=ctk.CTkFont(size=12),
            text_color="#95a5a6",
        )
        self._update_status.pack(side="left", padx=8)

    def _on_check_update(self) -> None:
        from ...core.update_checker import check_for_update

        self._update_btn.configure(state="disabled", text="Checking...")
        self._update_status.configure(text="", text_color="#95a5a6")

        def _callback(new_version: str, url: str) -> None:
            def _show():
                self._update_btn.configure(state="normal", text="Check for Updates")
                self._update_status.configure(
                    text=f"v{new_version} available!",
                    text_color="#2d8a4e",
                )
                self.app._show_update_banner(new_version, url)
            self.after(0, _show)

        def _on_timeout() -> None:
            if self._update_btn.cget("text") == "Checking...":
                self._update_btn.configure(state="normal", text="Check for Updates")
                self._update_status.configure(
                    text=f"You're up to date (v{__version__})",
                    text_color="#95a5a6",
                )

        check_for_update(__version__, _callback)
        self.after(5000, _on_timeout)

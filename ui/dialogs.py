"""
Diálogos modales personalizados para easyPDF.
"""
import tkinter as tk
from ui.styles import (
    COLORS, FONTS,
    create_styled_button, create_styled_label, create_styled_entry,
    create_styled_frame, create_styled_labelframe, create_styled_checkbutton
)


class SaveTOCDialog:
    """Diálogo modal para configurar la inclusión y formato de la página de índice al guardar."""

    def __init__(self, parent, has_bookmarks=True):
        self.parent = parent
        self.has_bookmarks = has_bookmarks
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Guardar PDF - easyPDF")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=COLORS['bg_dark'])
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Variables de estado
        self.include_toc_var = tk.BooleanVar(value=self.has_bookmarks)
        self.title_var = tk.StringVar(value="Índice")
        self.subtitle_var = tk.StringVar(value="Tabla de contenidos")

        self._build_ui()

        # Tamaño y posición tras construir
        self.dialog.update_idletasks()
        self._center_window(490, 345)

        # Atajos de teclado
        self.dialog.bind("<Return>", lambda e: self._on_confirm())
        self.dialog.bind("<Escape>", lambda e: self._on_cancel())

        # Esperar hasta que se cierre el diálogo
        self.parent.wait_window(self.dialog)

    def _center_window(self, width, height):
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.update_idletasks()
        p_x = self.parent.winfo_rootx()
        p_y = self.parent.winfo_rooty()
        p_w = self.parent.winfo_width()
        p_h = self.parent.winfo_height()
        x = p_x + (p_w - width) // 2
        y = p_y + (p_h - height) // 2
        self.dialog.geometry(f"{width}x{height}+{max(0, x)}+{max(0, y)}")

    def _build_ui(self):
        # ── Cabecera ──────────────────────────────────────────────────────
        header = create_styled_frame(self.dialog, 'medium')
        header.pack(fill="x")
        create_styled_label(
            header, "💾 Guardar Documento PDF",
            style='title', bg=COLORS['bg_medium']
        ).pack(pady=10, padx=15, anchor="w")

        # ── Botones de acción (van PRIMERO con side=bottom) ───────────────
        btn_frame = create_styled_frame(self.dialog, 'dark')
        btn_frame.pack(fill="x", side="bottom", padx=20, pady=12)

        create_styled_button(
            btn_frame, "Guardar...", self._on_confirm, 'success', width=12
        ).pack(side="right", padx=(5, 0))
        create_styled_button(
            btn_frame, "Cancelar", self._on_cancel, 'normal', width=10
        ).pack(side="right")

        # ── Contenido principal ───────────────────────────────────────────
        content = create_styled_frame(self.dialog, 'dark')
        content.pack(fill="both", expand=True, padx=20, pady=(8, 0))

        # Checkbox para activar/desactivar índice
        cb_frame = create_styled_frame(content, 'dark')
        cb_frame.pack(fill="x", pady=(4, 8))

        if self.has_bookmarks:
            self.cb_toc = create_styled_checkbutton(
                cb_frame,
                "Añadir página de índice al inicio (Página 0)",
                self.include_toc_var,
                self._on_toggle_toc
            )
            self.cb_toc.pack(anchor="w")
        else:
            self.include_toc_var.set(False)
            create_styled_label(
                cb_frame,
                "ℹ️ No hay marcadores definidos — el índice no estará disponible",
                style='muted'
            ).pack(anchor="w")

        # Caja de opciones de índice
        self.options_frame = create_styled_labelframe(content, "Opciones del Índice")
        self.options_frame.pack(fill="x", pady=(0, 8))

        inner = create_styled_frame(self.options_frame, 'medium')
        inner.pack(fill="x", padx=12, pady=10)

        # Fila Título
        row_title = create_styled_frame(inner, 'medium')
        row_title.pack(fill="x", pady=3)
        create_styled_label(row_title, "Título:", bg=COLORS['bg_medium'], width=10).pack(side="left")
        self.title_entry = create_styled_entry(row_title, textvariable=self.title_var, width=30)
        self.title_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Fila Subtítulo
        row_sub = create_styled_frame(inner, 'medium')
        row_sub.pack(fill="x", pady=3)
        create_styled_label(row_sub, "Subtítulo:", bg=COLORS['bg_medium'], width=10).pack(side="left")
        self.subtitle_entry = create_styled_entry(row_sub, textvariable=self.subtitle_var, width=30)
        self.subtitle_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Nota informativa
        create_styled_label(
            inner,
            "🔗 Cada entrada del índice incluirá un hiperenlace clicable.",
            style='muted', bg=COLORS['bg_medium']
        ).pack(anchor="w", pady=(6, 0))

        self._on_toggle_toc()

    def _on_toggle_toc(self):
        state = 'normal' if (self.has_bookmarks and self.include_toc_var.get()) else 'disabled'
        self.title_entry.config(state=state)
        self.subtitle_entry.config(state=state)

    def _on_confirm(self):
        self.result = {
            'include_toc': self.include_toc_var.get() and self.has_bookmarks,
            'title': self.title_var.get().strip() or "Índice",
            'subtitle': self.subtitle_var.get().strip()
        }
        self.dialog.destroy()

    def _on_cancel(self):
        self.result = None
        self.dialog.destroy()

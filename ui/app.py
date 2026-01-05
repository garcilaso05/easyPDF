"""
Clase principal de la aplicación PDF Editor.
"""
import io
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

from ui.panels import build_left_panel, build_center_panel, build_right_panel
from ui.styles import (
    COLORS, FONTS, apply_theme,
    create_styled_button, create_styled_frame, create_styled_checkbutton,
    create_styled_label
)
from logic.pdf_handler import PDFHandler
from logic.bookmarks import BookmarkManager
from logic.page_order import PageOrderManager
from logic.page_editor import PageEditor


class PDFEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("easyPDF - Editor Profesional")
        self.root.geometry("1100x700")

        # Aplicar tema oscuro
        apply_theme(root)

        # Managers de lógica
        self.pdf_handler = PDFHandler()
        self.bookmark_manager = BookmarkManager()
        self.page_order_manager = PageOrderManager()
        self.page_editor = PageEditor()

        # Estado de la UI
        self.doc = None
        self.thumbnails = []
        self.current_page = None
        self.order_mode = False
        self.edit_mode = False
        self.preview_zoom = 1.0
        self.preview_image = None
        self.original_preview_image = None
        self.result_preview_image = None

        self.build_ui()

    def build_ui(self):
        """Construye la interfaz de usuario"""
        # Barra superior
        top = create_styled_frame(self.root, 'medium')
        top.pack(fill="x", padx=0, pady=0)

        # Contenedor interno con padding
        top_inner = create_styled_frame(top, 'medium')
        top_inner.pack(fill="x", padx=15, pady=10)

        # Logo/Título
        title_frame = create_styled_frame(top_inner, 'medium')
        title_frame.pack(side="left", padx=(0, 20))
        tk.Label(title_frame, text="📄 easyPDF", font=('Segoe UI', 14, 'bold'),
                bg=COLORS['bg_medium'], fg=COLORS['accent_primary']).pack()

        # Botones de archivo
        create_styled_button(top_inner, "📂 Cargar", self.load_pdf, 'normal').pack(side="left", padx=3)
        create_styled_button(top_inner, "💾 Guardar", self.save_pdf, 'success').pack(side="left", padx=3)

        # Separador
        sep1 = create_styled_frame(top_inner, 'light', width=2)
        sep1.pack(side="left", fill="y", padx=15, pady=5)

        # Botones para añadir contenido
        create_styled_button(top_inner, "📑 PDFs", self.merge_multiple_pdfs, 'warning').pack(side="left", padx=3)
        create_styled_button(top_inner, "🖼️ Imágenes", self.add_images, 'accent').pack(side="left", padx=3)
        create_styled_button(top_inner, "📝 Docs", self.add_documents, 'accent').pack(side="left", padx=3)

        # Separador
        sep2 = create_styled_frame(top_inner, 'light', width=2)
        sep2.pack(side="left", fill="y", padx=15, pady=5)

        # Modos
        self.order_mode_var = tk.BooleanVar(value=False)
        self.order_switch = create_styled_checkbutton(top_inner, "🔀 Ordenar",
                                                      self.order_mode_var, self.toggle_order_mode)
        self.order_switch.config(bg=COLORS['bg_medium'])
        self.order_switch.pack(side="left", padx=8)

        self.edit_mode_var = tk.BooleanVar(value=False)
        self.edit_switch = create_styled_checkbutton(top_inner, "✏️ Editar",
                                                     self.edit_mode_var, self.toggle_edit_mode)
        self.edit_switch.config(bg=COLORS['bg_medium'])
        self.edit_switch.pack(side="left", padx=8)

        # Contenedor principal con 3 paneles
        main = tk.PanedWindow(self.root, orient="horizontal",
                             bg=COLORS['border'], sashwidth=4, sashpad=2)
        main.pack(fill="both", expand=True, padx=5, pady=5)

        # Construir paneles
        left_frame = build_left_panel(main, self)
        center_frame = build_center_panel(main, self)
        right_frame = build_right_panel(main, self)

        main.add(left_frame)
        main.add(center_frame)
        main.add(right_frame)

    # =========================================================================
    # CARGA Y GUARDADO
    # =========================================================================

    def load_pdf(self):
        """Carga un archivo PDF"""
        doc, toc = self.pdf_handler.load()
        if not doc:
            return

        self.doc = doc
        self.bookmark_manager.set_toc(toc)
        self.page_order_manager.initialize(len(doc))
        self.current_page = None

        self.load_thumbnails()
        self.refresh_tree()
        self.page_label.config(text="Selecciona una página")
        self.page_bookmarks_list.delete(0, tk.END)

    def save_pdf(self):
        """Guarda el PDF"""
        if not self.doc:
            messagebox.showwarning("Aviso", "No hay ningún PDF cargado")
            return

        # Aplicar reordenación si es necesario
        if self.page_order_manager.has_changes():
            new_toc = self.page_order_manager.apply_reorder(
                self.doc,
                self.bookmark_manager.get_toc()
            )
            self.bookmark_manager.set_toc(new_toc)

        # Aplicar transformaciones de página (escala)
        if self.page_editor.has_pending_transforms():
            self.page_editor.apply_all_transforms(self.doc)

        # Normalizar jerarquía
        normalized_toc = self.bookmark_manager.normalize_hierarchy()

        # Guardar
        if self.pdf_handler.save(self.doc, normalized_toc):
            self.bookmark_manager.set_toc(normalized_toc)
            self.refresh_tree()
            self.load_thumbnails()

    def merge_multiple_pdfs(self):
        """Fusiona múltiples PDFs seleccionados con el actual"""
        paths = filedialog.askopenfilenames(
            title="Selecciona PDFs para fusionar",
            filetypes=[("PDF", "*.pdf")]
        )
        if not paths:
            return

        total_added = 0
        for path in paths:
            result = self.pdf_handler.merge_single(
                self.doc,
                self.bookmark_manager.get_toc(),
                self.page_order_manager.get_order(),
                path
            )

            if result:
                self.doc, toc, page_order = result
                self.bookmark_manager.set_toc(toc)
                self.page_order_manager.set_order(page_order)
                total_added += 1

        if total_added > 0:
            self.load_thumbnails()
            self.refresh_tree()
            messagebox.showinfo("OK", f"Se añadieron {total_added} PDF(s). Total de páginas: {len(self.doc)}")

    def add_images(self):
        """Añade imágenes como nuevas páginas al PDF"""
        paths = filedialog.askopenfilenames(
            title="Selecciona imágenes para añadir",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.tif *.webp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("BMP", "*.bmp"),
                ("GIF", "*.gif"),
                ("TIFF", "*.tiff *.tif"),
                ("WebP", "*.webp"),
                ("Todos los archivos", "*.*")
            ]
        )
        if not paths:
            return

        result = self.pdf_handler.add_images_as_pages(
            self.doc,
            self.page_order_manager.get_order(),
            paths
        )

        if result:
            self.doc, page_order, added_count = result
            self.page_order_manager.set_order(page_order)
            self.load_thumbnails()
            self.refresh_tree()
            messagebox.showinfo("OK", f"Se añadieron {added_count} imagen(es) como páginas. Total: {len(self.doc)}")

    def add_documents(self):
        """Añade documentos Word/ODT como páginas PDF"""
        paths = filedialog.askopenfilenames(
            title="Selecciona documentos para añadir",
            filetypes=[
                ("Documentos", "*.doc *.docx *.odt *.rtf"),
                ("Word", "*.doc *.docx"),
                ("Word antiguo", "*.doc"),
                ("Word nuevo", "*.docx"),
                ("OpenDocument", "*.odt"),
                ("Rich Text", "*.rtf"),
                ("Todos los archivos", "*.*")
            ]
        )
        if not paths:
            return

        # Mostrar mensaje de espera (la conversión puede tardar)
        self.root.config(cursor="wait")
        self.root.update()

        try:
            result = self.pdf_handler.add_documents_as_pages(
                self.doc,
                self.bookmark_manager.get_toc(),
                self.page_order_manager.get_order(),
                paths
            )

            if result:
                self.doc, toc, page_order, added_count = result
                self.bookmark_manager.set_toc(toc)
                self.page_order_manager.set_order(page_order)
                self.load_thumbnails()
                self.refresh_tree()
                messagebox.showinfo("OK", f"Se añadieron {added_count} documento(s) como páginas. Total: {len(self.doc)}")
            else:
                messagebox.showwarning("Aviso",
                    "No se pudo convertir ningún documento.\n\n"
                    "Asegúrate de tener instalado:\n"
                    "- LibreOffice (recomendado)\n"
                    "- O Microsoft Word")
        finally:
            self.root.config(cursor="")

    # Mantener compatibilidad con el botón antiguo si existe
    def merge_pdf(self):
        """Fusiona otro PDF con el actual (compatibilidad)"""
        self.merge_multiple_pdfs()

    # =========================================================================
    # MINIATURAS
    # =========================================================================

    def load_thumbnails(self):
        """Carga las miniaturas de todas las páginas"""
        for widget in self.thumb_frame.winfo_children():
            widget.destroy()
        self.thumbnails = []

        page_order = self.page_order_manager.get_order()

        if not self.doc or not page_order:
            return

        for idx, page_num in enumerate(page_order):
            pix = self.pdf_handler.get_page_pixmap(self.doc, page_num, scale=0.15)
            if not pix:
                continue

            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            photo = ImageTk.PhotoImage(img)
            self.thumbnails.append(photo)

            thumb_item = create_styled_frame(self.thumb_frame, 'medium', padx=5, pady=4)
            thumb_item.pack(fill="x", pady=2, padx=3)

            row_frame = create_styled_frame(thumb_item, 'medium')
            row_frame.pack(fill="x")

            # Botones de ordenar (solo en modo ordenar)
            if self.order_mode:
                btn_order_frame = create_styled_frame(row_frame, 'medium')
                btn_order_frame.pack(side="left", padx=2)

                tk.Button(btn_order_frame, text="⬆", width=2, font=("Segoe UI", 7),
                         command=lambda i=idx: self.move_page_up(i),
                         bg=COLORS['button_bg'], fg=COLORS['text_primary'],
                         relief='flat').pack(pady=1)
                tk.Button(btn_order_frame, text="⬇", width=2, font=("Segoe UI", 7),
                         command=lambda i=idx: self.move_page_down(i),
                         bg=COLORS['button_bg'], fg=COLORS['text_primary'],
                         relief='flat').pack(pady=1)

            # Botones de editar página (solo en modo editar)
            if self.edit_mode:
                btn_edit_frame = create_styled_frame(row_frame, 'medium')
                btn_edit_frame.pack(side="left", padx=2)

                tk.Button(btn_edit_frame, text="↶", width=2, font=("Segoe UI", 7),
                         command=lambda p=page_num: self.rotate_page_left(p),
                         bg=COLORS['accent_primary'], fg=COLORS['text_primary'],
                         relief='flat').pack(pady=1)
                tk.Button(btn_edit_frame, text="↷", width=2, font=("Segoe UI", 7),
                         command=lambda p=page_num: self.rotate_page_right(p),
                         bg=COLORS['accent_primary'], fg=COLORS['text_primary'],
                         relief='flat').pack(pady=1)

            # Miniatura
            if self.order_mode:
                btn = tk.Button(row_frame, image=photo,
                               command=lambda p=page_num: self.show_preview(p),
                               relief="flat", bd=0, bg=COLORS['bg_medium'],
                               cursor='hand2')
            elif self.edit_mode:
                btn = tk.Button(row_frame, image=photo,
                               command=lambda p=page_num: self.show_edit_page(p),
                               relief="flat", bd=0, bg=COLORS['bg_medium'],
                               cursor='hand2')
            else:
                btn = tk.Button(row_frame, image=photo,
                               command=lambda p=page_num: self.select_page(p),
                               relief="flat", bd=0, bg=COLORS['bg_medium'],
                               cursor='hand2')
            btn.pack(side="left" if (self.order_mode or self.edit_mode) else None, padx=2)

            # Etiquetas
            info_frame = create_styled_frame(thumb_item, 'medium')
            info_frame.pack()

            if self.order_mode:
                lbl_text = f"Pos {idx + 1} (Pág. {page_num + 1})"
                lbl = tk.Label(info_frame, text=lbl_text, bg=COLORS['bg_medium'],
                              font=FONTS['small'], fg=COLORS['accent_secondary'])
            elif self.edit_mode:
                rotation = self.page_editor.get_page_rotation(self.doc, page_num)
                scale = self.page_editor.get_page_scale(page_num)
                lbl_text = f"Pág. {page_num + 1} | {rotation}°"
                if scale != 1.0:
                    lbl_text += f" | {int(scale*100)}%"
                lbl = tk.Label(info_frame, text=lbl_text, bg=COLORS['bg_medium'],
                              font=FONTS['small'], fg=COLORS['accent_primary'])
            else:
                lbl = tk.Label(info_frame, text=f"Pág. {page_num + 1}",
                              bg=COLORS['bg_medium'], font=FONTS['small'],
                              fg=COLORS['text_secondary'])
            lbl.pack()

            # Indicador de marcadores
            count = self.bookmark_manager.count_bookmarks_for_page(page_num + 1)
            if count > 0:
                tk.Label(info_frame, text=f"📑 {count}", bg=COLORS['bg_medium'],
                        fg=COLORS['accent_success'], font=FONTS['small']).pack()


    # =========================================================================
    # SELECCIÓN DE PÁGINA
    # =========================================================================

    def select_page(self, page_num):
        """Selecciona una página y muestra sus marcadores"""
        self.current_page = page_num + 1
        self.page_label.config(text=f"📄 Página {self.current_page} de {len(self.doc)}")

        self.page_bookmarks_list.delete(0, tk.END)
        for i, (lvl, title, page) in enumerate(self.bookmark_manager.get_toc()):
            if page == self.current_page:
                indent = "  " * (lvl - 1)
                self.page_bookmarks_list.insert(tk.END, f"{indent}[Nivel {lvl}] {title}")

        self.title_entry.delete(0, tk.END)
        self.level_entry.delete(0, tk.END)
        self.level_entry.insert(0, "1")

    # =========================================================================
    # MARCADORES
    # =========================================================================

    def on_bookmark_select(self, event):
        """Cuando se selecciona un marcador de la lista"""
        sel = self.page_bookmarks_list.curselection()
        if not sel:
            return

        page_bookmarks = self.bookmark_manager.get_bookmarks_for_page(self.current_page)
        if sel[0] < len(page_bookmarks):
            idx, (lvl, title, page) = page_bookmarks[sel[0]]
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, title)
            self.level_entry.delete(0, tk.END)
            self.level_entry.insert(0, str(lvl))

    def on_tree_select(self, event):
        """Cuando se selecciona un elemento del árbol"""
        sel = self.tree.selection()
        if not sel:
            return

        item = self.tree.item(sel[0])
        page = item["values"][0] if item["values"] else None
        if page:
            self.select_page(page - 1)
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, item["text"])

    def add_bookmark(self):
        """Añade un nuevo marcador"""
        if not self.current_page:
            messagebox.showwarning("Aviso", "Selecciona primero una página")
            return

        try:
            title = self.title_entry.get().strip()
            level = int(self.level_entry.get())
            if not title:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos")
            return

        self.bookmark_manager.add_bookmark(level, title, self.current_page)
        self.refresh_tree()
        self.select_page(self.current_page - 1)
        self.load_thumbnails()
        messagebox.showinfo("OK", f"Marcador añadido en página {self.current_page}")

    def update_bookmark(self):
        """Modifica el marcador seleccionado"""
        sel = self.page_bookmarks_list.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un marcador de la lista")
            return

        try:
            title = self.title_entry.get().strip()
            level = int(self.level_entry.get())
            if not title:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos")
            return

        page_bookmarks = self.bookmark_manager.get_bookmarks_for_page(self.current_page)
        if sel[0] < len(page_bookmarks):
            idx = page_bookmarks[sel[0]][0]
            self.bookmark_manager.update_bookmark(idx, level, title, self.current_page)
            self.refresh_tree()
            self.select_page(self.current_page - 1)

    def delete_bookmark(self):
        """Elimina el marcador seleccionado"""
        sel = self.page_bookmarks_list.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un marcador de la lista")
            return

        page_bookmarks = self.bookmark_manager.get_bookmarks_for_page(self.current_page)
        if sel[0] < len(page_bookmarks):
            idx = page_bookmarks[sel[0]][0]
            self.bookmark_manager.delete_bookmark(idx)
            self.refresh_tree()
            self.select_page(self.current_page - 1)
            self.load_thumbnails()

    def refresh_tree(self):
        """Actualiza el árbol de marcadores"""
        self.tree.delete(*self.tree.get_children())

        page_order = self.page_order_manager.get_order()
        display_toc = self.bookmark_manager.prepare_for_display(page_order)

        if not display_toc:
            return

        parent_stack = [""]

        for i, (lvl, title, page) in enumerate(display_toc):
            while len(parent_stack) < lvl:
                parent_stack.append(parent_stack[-1])
            parent_stack = parent_stack[:lvl]

            parent = parent_stack[-1] if parent_stack else ""
            item_id = self.tree.insert(parent, "end", iid=str(i), text=title, values=(page,))

            if len(parent_stack) <= lvl:
                parent_stack.append(item_id)
            else:
                parent_stack[lvl] = item_id

    # =========================================================================
    # MODO ORDENAR
    # =========================================================================

    def toggle_order_mode(self):
        """Alterna entre modo marcadores y modo ordenar"""
        self.order_mode = self.order_mode_var.get()

        # Si se activa modo ordenar, desactivar modo editar
        if self.order_mode and self.edit_mode:
            self.edit_mode_var.set(False)
            self.edit_mode = False
            self.edit_frame.pack_forget()

        if self.order_mode:
            self.bookmarks_frame.pack_forget()
            self.preview_frame.pack(fill="both", expand=True)
            self.page_label.config(text="🔀 Modo Ordenar - Selecciona una página para ver")
        else:
            self.preview_frame.pack_forget()
            self.bookmarks_frame.pack(fill="both", expand=True)
            self.page_label.config(text="Selecciona una página")

        if self.doc:
            self.load_thumbnails()

    def move_page_up(self, idx):
        """Mueve una página hacia arriba"""
        if self.page_order_manager.move_up(idx):
            self.load_thumbnails()
            self.refresh_tree()

    def move_page_down(self, idx):
        """Mueve una página hacia abajo"""
        if self.page_order_manager.move_down(idx):
            self.load_thumbnails()
            self.refresh_tree()

    # =========================================================================
    # VISTA PREVIA
    # =========================================================================

    def show_preview(self, page_num):
        """Muestra la vista previa de una página"""
        if not self.doc:
            return

        self.current_page = page_num + 1
        self.page_label.config(text=f"🔀 Vista previa: Página {self.current_page}")
        self.render_preview()

    def render_preview(self):
        """Renderiza la página actual con el zoom actual"""
        if not self.doc or not self.current_page:
            return

        pix = self.pdf_handler.get_page_pixmap(self.doc, self.current_page - 1, self.preview_zoom)
        if not pix:
            return

        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        self.preview_image = ImageTk.PhotoImage(img)

        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(0, 0, anchor="nw", image=self.preview_image)
        self.preview_canvas.configure(scrollregion=(0, 0, pix.width, pix.height))
        self.zoom_label.config(text=f"{int(self.preview_zoom * 100)}%")

    def zoom_in(self):
        """Aumentar zoom"""
        self.preview_zoom = min(self.preview_zoom + 0.25, 4.0)
        self.render_preview()

    def zoom_out(self):
        """Reducir zoom"""
        self.preview_zoom = max(self.preview_zoom - 0.25, 0.25)
        self.render_preview()

    def zoom_fit(self):
        """Ajustar zoom al tamaño del canvas"""
        if not self.doc or not self.current_page:
            return

        page_rect = self.pdf_handler.get_page_rect(self.doc, self.current_page - 1)
        if not page_rect:
            return

        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()

        scale_w = canvas_width / page_rect.width
        scale_h = canvas_height / page_rect.height

        self.preview_zoom = min(scale_w, scale_h, 2.0)
        self.render_preview()

    def on_preview_zoom(self, event):
        """Zoom con Ctrl + rueda del ratón"""
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def on_preview_scroll(self, event):
        """Scroll vertical en la vista previa"""
        self.preview_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # =========================================================================
    # MODO EDITAR PÁGINAS
    # =========================================================================

    def toggle_edit_mode(self):
        """Alterna entre modo normal y modo editar páginas"""
        self.edit_mode = self.edit_mode_var.get()

        # Si se activa modo editar, desactivar modo ordenar
        if self.edit_mode and self.order_mode:
            self.order_mode_var.set(False)
            self.order_mode = False

        if self.edit_mode:
            self.bookmarks_frame.pack_forget()
            self.edit_frame.pack(fill="both", expand=True)
            self.page_label.config(text="✏️ Modo Editar - Selecciona una página")
        else:
            self.edit_frame.pack_forget()
            self.bookmarks_frame.pack(fill="both", expand=True)
            self.page_label.config(text="Selecciona una página")

        if self.doc:
            self.load_thumbnails()

    def show_edit_page(self, page_num):
        """Muestra la página seleccionada para edición"""
        if not self.doc:
            return

        self.current_page = page_num + 1

        # Guardar tamaño original para comparación
        width, height = self.page_editor.get_page_size(self.doc, page_num)
        rotation = self.page_editor.get_page_rotation(self.doc, page_num)
        scale = self.page_editor.get_page_scale(page_num)
        margins = self.page_editor.get_page_margins(page_num)
        grayscale = self.page_editor.get_page_grayscale(page_num)

        # Calcular tamaño resultado
        result_width = width * scale + margins['left'] + margins['right']
        result_height = height * scale + margins['top'] + margins['bottom']

        self.page_label.config(
            text=f"✏️ Página {self.current_page} | Rotación: {rotation}°"
        )

        # Actualizar slider de escala
        self.scale_slider.set(scale * 100)
        self.update_scale_label(scale * 100)

        # Actualizar controles de márgenes
        if self.uniform_margins_var.get():
            self.uniform_margin_slider.set(margins['top'])
        else:
            self.margin_top_entry.delete(0, tk.END)
            self.margin_top_entry.insert(0, str(int(margins['top'])))
            self.margin_bottom_entry.delete(0, tk.END)
            self.margin_bottom_entry.insert(0, str(int(margins['bottom'])))
            self.margin_left_entry.delete(0, tk.END)
            self.margin_left_entry.insert(0, str(int(margins['left'])))
            self.margin_right_entry.delete(0, tk.END)
            self.margin_right_entry.insert(0, str(int(margins['right'])))

        # Actualizar checkbox de B/N
        self.grayscale_var.set(grayscale)

        # Actualizar etiquetas de tamaño
        self.original_size_label.config(text=f"Original: {width:.0f} x {height:.0f} px")
        self.result_size_label.config(text=f"Resultado: {result_width:.0f} x {result_height:.0f} px")

        # Mostrar vista previa (antes y después)
        self.render_edit_preview()

    def render_edit_preview(self):
        """Renderiza la vista previa de la página en modo edición (antes/después)"""
        if not self.doc or not self.current_page:
            return

        page_num = self.current_page - 1
        scale = self.page_editor.get_page_scale(page_num)
        margins = self.page_editor.get_page_margins(page_num)
        grayscale = self.page_editor.get_page_grayscale(page_num)

        # Calcular escala de visualización para que quepa en el canvas
        canvas_width = max(self.original_canvas.winfo_width(), 150)
        canvas_height = max(self.original_canvas.winfo_height(), 150)

        # === RENDERIZAR ORIGINAL (estado guardado o actual sin transformaciones) ===
        original_data = self.page_editor.get_original_pixmap_data(page_num)

        if original_data:
            # Usar el estado original guardado
            img_original = Image.open(io.BytesIO(original_data['pixmap_bytes']))
            # Redimensionar para que quepa
            orig_w, orig_h = img_original.size
            fit_scale = min(canvas_width / orig_w, canvas_height / orig_h, 1.0) * 0.9
            new_size = (int(orig_w * fit_scale), int(orig_h * fit_scale))
            img_original = img_original.resize(new_size, Image.Resampling.LANCZOS)
            self.original_preview_image = ImageTk.PhotoImage(img_original)
        else:
            # No hay estado guardado, usar la página actual
            page_rect = self.pdf_handler.get_page_rect(self.doc, page_num)
            if not page_rect:
                return
            fit_scale = min(canvas_width / page_rect.width, canvas_height / page_rect.height, 1.0) * 0.9
            pix_original = self.pdf_handler.get_page_pixmap(self.doc, page_num, fit_scale)
            if pix_original:
                img_original = Image.frombytes("RGB", (pix_original.width, pix_original.height), pix_original.samples)
                self.original_preview_image = ImageTk.PhotoImage(img_original)

        if self.original_preview_image:
            self.original_canvas.delete("all")
            img_w = self.original_preview_image.width()
            img_h = self.original_preview_image.height()
            x = max(0, (canvas_width - img_w) // 2)
            y = max(0, (canvas_height - img_h) // 2)
            self.original_canvas.create_image(x, y, anchor="nw", image=self.original_preview_image)
            self.original_canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))

        # === RENDERIZAR RESULTADO (con todas las transformaciones aplicadas visualmente) ===
        page_rect = self.pdf_handler.get_page_rect(self.doc, page_num)
        if not page_rect:
            return

        fit_scale = min(canvas_width / page_rect.width, canvas_height / page_rect.height, 1.0) * 0.9

        # Renderizar la página actual (que puede tener rotación aplicada)
        pix_result = self.pdf_handler.get_page_pixmap(self.doc, page_num, fit_scale)
        if pix_result:
            img_result = Image.frombytes("RGB", (pix_result.width, pix_result.height), pix_result.samples)

            # Aplicar escala de grises si está activado
            if grayscale:
                img_result = img_result.convert('L').convert('RGB')

            # Aplicar escala visual
            if scale != 1.0:
                new_w = int(img_result.width * scale)
                new_h = int(img_result.height * scale)
                # Limitar tamaño máximo para la vista previa
                max_size = max(canvas_width, canvas_height) * 1.5
                if new_w > max_size or new_h > max_size:
                    ratio = min(max_size / new_w, max_size / new_h)
                    new_w = int(new_w * ratio)
                    new_h = int(new_h * ratio)
                img_result = img_result.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Aplicar márgenes visuales (añadir borde blanco)
            if any(v > 0 for v in margins.values()):
                margin_scale = fit_scale  # Escalar márgenes a la vista previa
                m_top = int(margins['top'] * margin_scale)
                m_right = int(margins['right'] * margin_scale)
                m_bottom = int(margins['bottom'] * margin_scale)
                m_left = int(margins['left'] * margin_scale)

                new_width = img_result.width + m_left + m_right
                new_height = img_result.height + m_top + m_bottom

                # Crear imagen con márgenes blancos
                img_with_margins = Image.new('RGB', (new_width, new_height), (255, 255, 255))
                img_with_margins.paste(img_result, (m_left, m_top))
                img_result = img_with_margins

            self.result_preview_image = ImageTk.PhotoImage(img_result)

            self.edit_canvas.delete("all")
            img_w = self.result_preview_image.width()
            img_h = self.result_preview_image.height()
            x = max(0, (canvas_width - img_w) // 2)
            y = max(0, (canvas_height - img_h) // 2)
            self.edit_canvas.create_image(x, y, anchor="nw", image=self.result_preview_image)
            self.edit_canvas.configure(scrollregion=(0, 0, max(canvas_width, img_w),
                                                      max(canvas_height, img_h)))

    def rotate_page_left(self, page_num):
        """Rota la página 90° a la izquierda"""
        if self.page_editor.rotate_page(self.doc, page_num, 'left'):
            self.load_thumbnails()
            if self.current_page == page_num + 1:
                self.show_edit_page(page_num)

    def rotate_page_right(self, page_num):
        """Rota la página 90° a la derecha"""
        if self.page_editor.rotate_page(self.doc, page_num, 'right'):
            self.load_thumbnails()
            if self.current_page == page_num + 1:
                self.show_edit_page(page_num)

    def on_scale_change(self, value):
        """Cuando cambia el slider de escala"""
        if not self.current_page:
            return

        scale = float(value) / 100.0
        page_num = self.current_page - 1

        self.page_editor.set_page_scale(page_num, scale)
        self.update_scale_label(float(value))

        # Actualizar etiquetas de tamaño (incluyendo márgenes)
        self._update_size_with_margins()

        # Actualizar vista previa
        self.render_edit_preview()
        self.load_thumbnails()

    def update_scale_label(self, value):
        """Actualiza la etiqueta del slider de escala"""
        self.scale_value_label.config(text=f"{int(value)}%")

    def reset_page_scale(self):
        """Resetea la escala de la página actual a 100%"""
        if not self.current_page:
            return

        page_num = self.current_page - 1
        self.page_editor.clear_page_scale(page_num)
        self.scale_slider.set(100)
        self.update_scale_label(100)

        # Actualizar vista previa
        self.show_edit_page(page_num)
        self.load_thumbnails()

    # =========================================================================
    # MÁRGENES
    # =========================================================================

    def toggle_uniform_margins(self):
        """Alterna entre márgenes uniformes e individuales"""
        if self.uniform_margins_var.get():
            self.individual_margins_frame.pack_forget()
            self.uniform_margin_frame.pack(fill="x", pady=3)
        else:
            self.uniform_margin_frame.pack_forget()
            self.individual_margins_frame.pack(fill="x", pady=3)

    def on_uniform_margin_change(self, value):
        """Cuando cambia el slider de margen uniforme"""
        if not self.current_page:
            return

        margin = int(float(value))
        page_num = self.current_page - 1

        self.page_editor.set_page_margins_uniform(page_num, margin)
        self._update_size_with_margins()
        self.render_edit_preview()

    def on_individual_margin_change(self, event=None):
        """Cuando cambian los márgenes individuales"""
        if not self.current_page:
            return

        try:
            top = int(self.margin_top_entry.get() or 0)
            bottom = int(self.margin_bottom_entry.get() or 0)
            left = int(self.margin_left_entry.get() or 0)
            right = int(self.margin_right_entry.get() or 0)
        except ValueError:
            return

        page_num = self.current_page - 1
        self.page_editor.set_page_margins(page_num, top, right, bottom, left)
        self._update_size_with_margins()
        self.render_edit_preview()

    def _update_size_with_margins(self):
        """Actualiza las etiquetas de tamaño incluyendo márgenes"""
        if not self.current_page:
            return

        page_num = self.current_page - 1
        width, height = self.page_editor.get_page_size(self.doc, page_num)
        scale = self.page_editor.get_page_scale(page_num)
        margins = self.page_editor.get_page_margins(page_num)

        result_width = width * scale + margins['left'] + margins['right']
        result_height = height * scale + margins['top'] + margins['bottom']

        self.original_size_label.config(text=f"Original: {width:.0f} x {height:.0f} px")
        self.result_size_label.config(text=f"Resultado: {result_width:.0f} x {result_height:.0f} px")

    def reset_margins(self):
        """Elimina los márgenes de la página actual"""
        if not self.current_page:
            return

        page_num = self.current_page - 1
        self.page_editor.clear_page_margins(page_num)

        # Resetear controles
        self.uniform_margin_slider.set(0)
        self.margin_top_entry.delete(0, tk.END)
        self.margin_top_entry.insert(0, "0")
        self.margin_bottom_entry.delete(0, tk.END)
        self.margin_bottom_entry.insert(0, "0")
        self.margin_left_entry.delete(0, tk.END)
        self.margin_left_entry.insert(0, "0")
        self.margin_right_entry.delete(0, tk.END)
        self.margin_right_entry.insert(0, "0")

        self._update_size_with_margins()
        self.render_edit_preview()

    # =========================================================================
    # BLANCO Y NEGRO
    # =========================================================================

    def toggle_grayscale(self):
        """Activa/desactiva la conversión a blanco y negro"""
        if not self.current_page:
            return

        page_num = self.current_page - 1
        enabled = self.grayscale_var.get()

        if enabled:
            self.page_editor.set_page_grayscale(page_num, True)
        else:
            self.page_editor.clear_page_grayscale(page_num)

        self.render_edit_preview()


"""
Módulo para construcción de paneles de la interfaz.
Tema: Azul oscuro profesional
"""
import tkinter as tk
from tkinter import ttk
from ui.styles import (
    COLORS, FONTS,
    create_styled_button, create_styled_label, create_styled_entry,
    create_styled_listbox, create_styled_frame, create_styled_labelframe,
    create_styled_canvas, create_styled_scale, create_styled_checkbutton
)


def build_left_panel(parent, app):
    """Construye el panel izquierdo con miniaturas de páginas"""
    left_frame = create_styled_frame(parent, 'dark', width=160)

    # Título del panel
    header = create_styled_frame(left_frame, 'medium')
    header.pack(fill="x", pady=(0, 5))
    create_styled_label(header, "📄 PÁGINAS", style='subtitle',
                       bg=COLORS['bg_medium']).pack(pady=8, padx=10)

    # Canvas con scrollbar para las miniaturas
    thumb_container = create_styled_frame(left_frame, 'dark')
    thumb_container.pack(fill="both", expand=True)

    thumb_canvas = create_styled_canvas(thumb_container, width=140)
    thumb_scrollbar = ttk.Scrollbar(thumb_container, orient="vertical", command=thumb_canvas.yview)
    thumb_frame = create_styled_frame(thumb_canvas, 'thumbnail')

    thumb_canvas.configure(yscrollcommand=thumb_scrollbar.set)
    thumb_scrollbar.pack(side="right", fill="y")
    thumb_canvas.pack(side="left", fill="both", expand=True)

    thumb_window = thumb_canvas.create_window((0, 0), window=thumb_frame, anchor="nw")
    thumb_frame.bind("<Configure>", lambda e: thumb_canvas.configure(scrollregion=thumb_canvas.bbox("all")))
    thumb_canvas.bind("<Configure>", lambda e: thumb_canvas.itemconfig(thumb_window, width=e.width))

    # Scroll con rueda del ratón
    def _on_mousewheel(e):
        thumb_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
    thumb_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # Guardar referencias en la app
    app.thumb_canvas = thumb_canvas
    app.thumb_frame = thumb_frame

    return left_frame


def build_center_panel(parent, app):
    """Construye el panel central con editor de marcadores y vista previa"""
    center_frame = create_styled_frame(parent, 'dark', width=350)

    # Header con título de página
    header = create_styled_frame(center_frame, 'medium')
    header.pack(fill="x", pady=(0, 10))

    app.page_label = create_styled_label(header, "Selecciona una página",
                                         style='subtitle', bg=COLORS['bg_medium'])
    app.page_label.pack(pady=10, padx=10)

    # --- Frame para modo MARCADORES ---
    app.bookmarks_frame = create_styled_frame(center_frame, 'dark')
    app.bookmarks_frame.pack(fill="both", expand=True, padx=10)

    create_styled_label(app.bookmarks_frame, "Marcadores en esta página:",
                       style='muted').pack(anchor="w", pady=(0, 5))

    app.page_bookmarks_list = create_styled_listbox(app.bookmarks_frame, height=6)
    app.page_bookmarks_list.pack(fill="x", pady=5)
    app.page_bookmarks_list.bind("<<ListboxSelect>>", app.on_bookmark_select)

    # Formulario de edición
    form_frame = create_styled_labelframe(app.bookmarks_frame, "✏️ Editar / Añadir marcador")
    form_frame.pack(fill="x", pady=10)

    inner_form = create_styled_frame(form_frame, 'medium')
    inner_form.pack(fill="x", padx=10, pady=10)

    # Título
    title_row = create_styled_frame(inner_form, 'medium')
    title_row.pack(fill="x", pady=3)
    create_styled_label(title_row, "Título:", bg=COLORS['bg_medium']).pack(side="left")
    app.title_entry = create_styled_entry(title_row, width=25)
    app.title_entry.pack(side="right", padx=5)

    # Nivel
    level_row = create_styled_frame(inner_form, 'medium')
    level_row.pack(fill="x", pady=3)
    create_styled_label(level_row, "Nivel (1=cap):", bg=COLORS['bg_medium']).pack(side="left")
    app.level_entry = create_styled_entry(level_row, width=8)
    app.level_entry.insert(0, "1")
    app.level_entry.pack(side="right", padx=5)

    # Botones
    btn_frame = create_styled_frame(inner_form, 'medium')
    btn_frame.pack(fill="x", pady=(10, 5))

    create_styled_button(btn_frame, "➕ Añadir", app.add_bookmark, 'success').pack(side="left", padx=2)
    create_styled_button(btn_frame, "✏️ Modificar", app.update_bookmark, 'accent').pack(side="left", padx=2)
    create_styled_button(btn_frame, "🗑️ Eliminar", app.delete_bookmark, 'danger').pack(side="left", padx=2)

    # --- Frame para modo VISTA PREVIA (inicialmente oculto) ---
    app.preview_frame = create_styled_frame(center_frame, 'dark')

    # Controles de zoom
    zoom_frame = create_styled_frame(app.preview_frame, 'medium')
    zoom_frame.pack(fill="x", pady=5, padx=10)

    create_styled_button(zoom_frame, "🔍−", app.zoom_out, 'normal', width=4).pack(side="left", padx=2)
    app.zoom_label = create_styled_label(zoom_frame, "100%", bg=COLORS['bg_medium'])
    app.zoom_label.pack(side="left", padx=10)
    create_styled_button(zoom_frame, "🔍+", app.zoom_in, 'normal', width=4).pack(side="left", padx=2)
    create_styled_button(zoom_frame, "Ajustar", app.zoom_fit, 'accent', width=8).pack(side="left", padx=10)

    # Canvas para vista previa con scroll
    preview_container = create_styled_frame(app.preview_frame, 'dark')
    preview_container.pack(fill="both", expand=True, padx=10)

    app.preview_canvas = create_styled_canvas(preview_container)
    preview_scroll_y = ttk.Scrollbar(preview_container, orient="vertical", command=app.preview_canvas.yview)
    preview_scroll_x = ttk.Scrollbar(preview_container, orient="horizontal", command=app.preview_canvas.xview)

    app.preview_canvas.configure(yscrollcommand=preview_scroll_y.set, xscrollcommand=preview_scroll_x.set)

    preview_scroll_y.pack(side="right", fill="y")
    preview_scroll_x.pack(side="bottom", fill="x")
    app.preview_canvas.pack(side="left", fill="both", expand=True)

    # Bind para zoom con rueda del ratón en preview
    app.preview_canvas.bind("<Control-MouseWheel>", app.on_preview_zoom)
    app.preview_canvas.bind("<MouseWheel>", app.on_preview_scroll)

    # --- Frame para modo EDITAR PÁGINAS (inicialmente oculto) ---
    app.edit_frame = create_styled_frame(center_frame, 'dark')

    # Contenedor con scroll para los controles de edición
    edit_controls_canvas = create_styled_canvas(app.edit_frame)
    edit_controls_scrollbar = ttk.Scrollbar(app.edit_frame, orient="vertical", command=edit_controls_canvas.yview)
    edit_controls_frame = create_styled_frame(edit_controls_canvas, 'dark')

    edit_controls_canvas.configure(yscrollcommand=edit_controls_scrollbar.set)
    edit_controls_scrollbar.pack(side="right", fill="y")
    edit_controls_canvas.pack(side="left", fill="both", expand=True)

    edit_controls_window = edit_controls_canvas.create_window((0, 0), window=edit_controls_frame, anchor="nw")
    edit_controls_frame.bind("<Configure>", lambda e: edit_controls_canvas.configure(scrollregion=edit_controls_canvas.bbox("all")))
    edit_controls_canvas.bind("<Configure>", lambda e: edit_controls_canvas.itemconfig(edit_controls_window, width=e.width))

    # Sección de rotación
    rotation_frame = create_styled_labelframe(edit_controls_frame, "🔄 Rotación")
    rotation_frame.pack(fill="x", pady=5, padx=10)

    rotation_btns = create_styled_frame(rotation_frame, 'medium')
    rotation_btns.pack(pady=10)

    create_styled_button(rotation_btns, "↶ Izquierda",
                        lambda: app.rotate_page_left(app.current_page - 1) if app.current_page else None,
                        'accent', width=12).pack(side="left", padx=5)
    create_styled_button(rotation_btns, "↷ Derecha",
                        lambda: app.rotate_page_right(app.current_page - 1) if app.current_page else None,
                        'accent', width=12).pack(side="left", padx=5)

    # Sección de escala/tamaño
    scale_frame = create_styled_labelframe(edit_controls_frame, "📐 Escala")
    scale_frame.pack(fill="x", pady=5, padx=10)

    scale_inner = create_styled_frame(scale_frame, 'medium')
    scale_inner.pack(fill="x", padx=10, pady=10)

    slider_frame = create_styled_frame(scale_inner, 'medium')
    slider_frame.pack(fill="x")

    create_styled_label(slider_frame, "25%", style='muted', bg=COLORS['bg_medium']).pack(side="left")
    app.scale_slider = create_styled_scale(slider_frame, from_=25, to=200, orient="horizontal",
                                           command=app.on_scale_change, showvalue=False, length=150)
    app.scale_slider.set(100)
    app.scale_slider.pack(side="left", fill="x", expand=True, padx=5)
    create_styled_label(slider_frame, "200%", style='muted', bg=COLORS['bg_medium']).pack(side="left")

    scale_info_frame = create_styled_frame(scale_inner, 'medium')
    scale_info_frame.pack(fill="x", pady=5)
    app.scale_value_label = tk.Label(scale_info_frame, text="100%",
                                     font=('Segoe UI', 14, 'bold'),
                                     fg=COLORS['accent_primary'], bg=COLORS['bg_medium'])
    app.scale_value_label.pack(side="left", padx=5)
    create_styled_button(scale_info_frame, "↺ Reset", app.reset_page_scale, 'normal').pack(side="right")

    # Sección de márgenes
    margin_frame = create_styled_labelframe(edit_controls_frame, "📏 Márgenes (puntos)")
    margin_frame.pack(fill="x", pady=5, padx=10)

    margin_inner = create_styled_frame(margin_frame, 'medium')
    margin_inner.pack(fill="x", padx=10, pady=10)

    # Checkbox para márgenes uniformes
    app.uniform_margins_var = tk.BooleanVar(value=True)
    create_styled_checkbutton(margin_inner, "Mismo margen en todos los lados",
                             app.uniform_margins_var, app.toggle_uniform_margins).pack(anchor="w")

    # Frame para margen uniforme
    app.uniform_margin_frame = create_styled_frame(margin_inner, 'medium')
    app.uniform_margin_frame.pack(fill="x", pady=5)
    create_styled_label(app.uniform_margin_frame, "Margen:", bg=COLORS['bg_medium']).pack(side="left")
    app.uniform_margin_slider = create_styled_scale(app.uniform_margin_frame, from_=0, to=100,
                                                    orient="horizontal", command=app.on_uniform_margin_change,
                                                    showvalue=True, length=150)
    app.uniform_margin_slider.pack(side="left", fill="x", expand=True, padx=5)

    # Frame para márgenes individuales (oculto por defecto)
    app.individual_margins_frame = create_styled_frame(margin_inner, 'medium')

    margins_grid = create_styled_frame(app.individual_margins_frame, 'medium')
    margins_grid.pack(pady=5)

    # Superior
    create_styled_label(margins_grid, "Superior:", bg=COLORS['bg_medium']).grid(row=0, column=0, sticky="e", padx=2)
    app.margin_top_entry = create_styled_entry(margins_grid, width=6)
    app.margin_top_entry.insert(0, "0")
    app.margin_top_entry.grid(row=0, column=1, padx=2, pady=2)
    app.margin_top_entry.bind("<KeyRelease>", app.on_individual_margin_change)

    # Inferior
    create_styled_label(margins_grid, "Inferior:", bg=COLORS['bg_medium']).grid(row=1, column=0, sticky="e", padx=2)
    app.margin_bottom_entry = create_styled_entry(margins_grid, width=6)
    app.margin_bottom_entry.insert(0, "0")
    app.margin_bottom_entry.grid(row=1, column=1, padx=2, pady=2)
    app.margin_bottom_entry.bind("<KeyRelease>", app.on_individual_margin_change)

    # Izquierdo
    create_styled_label(margins_grid, "Izq:", bg=COLORS['bg_medium']).grid(row=0, column=2, sticky="e", padx=(10, 2))
    app.margin_left_entry = create_styled_entry(margins_grid, width=6)
    app.margin_left_entry.insert(0, "0")
    app.margin_left_entry.grid(row=0, column=3, padx=2, pady=2)
    app.margin_left_entry.bind("<KeyRelease>", app.on_individual_margin_change)

    # Derecho
    create_styled_label(margins_grid, "Der:", bg=COLORS['bg_medium']).grid(row=1, column=2, sticky="e", padx=(10, 2))
    app.margin_right_entry = create_styled_entry(margins_grid, width=6)
    app.margin_right_entry.insert(0, "0")
    app.margin_right_entry.grid(row=1, column=3, padx=2, pady=2)
    app.margin_right_entry.bind("<KeyRelease>", app.on_individual_margin_change)

    create_styled_button(margin_inner, "↺ Quitar márgenes", app.reset_margins, 'normal').pack(pady=5)

    # Sección de blanco y negro
    bw_frame = create_styled_labelframe(edit_controls_frame, "🎨 Color")
    bw_frame.pack(fill="x", pady=5, padx=10)

    bw_inner = create_styled_frame(bw_frame, 'medium')
    bw_inner.pack(fill="x", padx=10, pady=10)

    app.grayscale_var = tk.BooleanVar(value=False)
    create_styled_checkbutton(bw_inner, "Convertir a Blanco y Negro",
                             app.grayscale_var, app.toggle_grayscale).pack(anchor="w")

    # Vista previa ANTES / DESPUÉS
    preview_label_frame = create_styled_frame(edit_controls_frame, 'dark')
    preview_label_frame.pack(fill="x", pady=(10, 5), padx=10)

    create_styled_label(preview_label_frame, "📄 Original", style='muted').pack(side="left", expand=True)
    create_styled_label(preview_label_frame, "📄 Resultado", style='accent').pack(side="left", expand=True)

    # Contenedor para los dos canvas lado a lado
    edit_preview_container = create_styled_frame(edit_controls_frame, 'dark')
    edit_preview_container.pack(fill="both", expand=True, padx=10, pady=5)

    # Canvas ORIGINAL (izquierda)
    original_frame = create_styled_frame(edit_preview_container, 'medium', bd=1, relief="solid")
    original_frame.pack(side="left", fill="both", expand=True, padx=(0, 3))

    app.original_canvas = create_styled_canvas(original_frame, height=180)
    original_scroll_y = ttk.Scrollbar(original_frame, orient="vertical", command=app.original_canvas.yview)
    app.original_canvas.configure(yscrollcommand=original_scroll_y.set)
    original_scroll_y.pack(side="right", fill="y")
    app.original_canvas.pack(side="left", fill="both", expand=True)

    # Canvas RESULTADO (derecha)
    result_frame = create_styled_frame(edit_preview_container, 'medium', bd=1, relief="solid")
    result_frame.pack(side="left", fill="both", expand=True, padx=(3, 0))

    app.edit_canvas = create_styled_canvas(result_frame, height=180)
    edit_scroll_y = ttk.Scrollbar(result_frame, orient="vertical", command=app.edit_canvas.yview)
    app.edit_canvas.configure(yscrollcommand=edit_scroll_y.set)
    edit_scroll_y.pack(side="right", fill="y")
    app.edit_canvas.pack(side="left", fill="both", expand=True)

    # Frame para mostrar información de tamaños
    size_info_frame = create_styled_frame(edit_controls_frame, 'dark')
    size_info_frame.pack(fill="x", pady=5, padx=10)

    app.original_size_label = create_styled_label(size_info_frame, "Original: --", style='muted')
    app.original_size_label.pack(side="left", expand=True)

    app.result_size_label = create_styled_label(size_info_frame, "Resultado: --", style='accent')
    app.result_size_label.pack(side="left", expand=True)

    return center_frame


def build_right_panel(parent, app):
    """Construye el panel derecho con el árbol de marcadores"""
    right_frame = create_styled_frame(parent, 'dark', width=280)

    # Header
    header = create_styled_frame(right_frame, 'medium')
    header.pack(fill="x", pady=(0, 5))
    create_styled_label(header, "🌳 ÁRBOL DE MARCADORES", style='subtitle',
                       bg=COLORS['bg_medium']).pack(pady=8, padx=10)

    tree_container = create_styled_frame(right_frame, 'dark')
    tree_container.pack(fill="both", expand=True, padx=5)

    # Configurar estilo del Treeview
    style = ttk.Style()
    style.configure("Dark.Treeview",
                   background=COLORS['bg_medium'],
                   foreground=COLORS['text_primary'],
                   fieldbackground=COLORS['bg_medium'],
                   font=FONTS['normal'])
    style.configure("Dark.Treeview.Heading",
                   background=COLORS['bg_light'],
                   foreground=COLORS['text_primary'],
                   font=FONTS['subtitle'])
    style.map("Dark.Treeview",
             background=[('selected', COLORS['accent_primary'])],
             foreground=[('selected', COLORS['text_primary'])])

    app.tree = ttk.Treeview(tree_container, columns=("page",), show="tree headings", style="Dark.Treeview")
    app.tree.heading("#0", text="Título")
    app.tree.heading("page", text="Pág.")
    app.tree.column("#0", width=200)
    app.tree.column("page", width=45)

    tree_scroll = ttk.Scrollbar(tree_container, orient="vertical", command=app.tree.yview)
    app.tree.configure(yscrollcommand=tree_scroll.set)

    app.tree.pack(side="left", fill="both", expand=True)
    tree_scroll.pack(side="right", fill="y")

    app.tree.bind("<<TreeviewSelect>>", app.on_tree_select)

    return right_frame

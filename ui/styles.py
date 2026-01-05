"""
Módulo de estilos y temas para la interfaz.
Tema: Azul oscuro profesional
"""
import tkinter as tk
from tkinter import ttk


# ============================================================================
# PALETA DE COLORES - AZUL OSCURO PROFESIONAL
# ============================================================================

COLORS = {
    # Fondos principales
    'bg_dark': '#1a2332',        # Fondo más oscuro
    'bg_medium': '#243447',      # Fondo medio
    'bg_light': '#2d4156',       # Fondo claro
    'bg_hover': '#3d5a80',       # Hover

    # Acentos
    'accent_primary': '#4a90d9',  # Azul principal
    'accent_secondary': '#5fa8d3', # Azul secundario
    'accent_success': '#4caf50',  # Verde éxito
    'accent_warning': '#ff9800',  # Naranja advertencia
    'accent_danger': '#e74c3c',   # Rojo peligro

    # Textos
    'text_primary': '#ffffff',    # Texto principal
    'text_secondary': '#b0bec5',  # Texto secundario
    'text_muted': '#78909c',      # Texto apagado

    # Bordes
    'border': '#3d5a80',          # Borde normal
    'border_light': '#4a6fa5',    # Borde claro

    # Especiales
    'thumbnail_bg': '#1e2d3d',    # Fondo miniaturas
    'input_bg': '#2d4156',        # Fondo inputs
    'button_bg': '#3d5a80',       # Fondo botones
    'scrollbar': '#4a6fa5',       # Scrollbar
}

# Fuentes
FONTS = {
    'title': ('Segoe UI', 12, 'bold'),
    'subtitle': ('Segoe UI', 10, 'bold'),
    'normal': ('Segoe UI', 9),
    'small': ('Segoe UI', 8),
    'button': ('Segoe UI', 9),
    'mono': ('Consolas', 9),
}


def apply_theme(root):
    """Aplica el tema oscuro a la ventana principal y configura ttk"""
    root.configure(bg=COLORS['bg_dark'])

    # Configurar estilos ttk
    style = ttk.Style()

    # Intentar usar un tema base que permita personalización
    try:
        style.theme_use('clam')
    except:
        pass

    # Frame
    style.configure('TFrame', background=COLORS['bg_dark'])
    style.configure('Dark.TFrame', background=COLORS['bg_dark'])
    style.configure('Medium.TFrame', background=COLORS['bg_medium'])
    style.configure('Light.TFrame', background=COLORS['bg_light'])

    # Label
    style.configure('TLabel',
                   background=COLORS['bg_dark'],
                   foreground=COLORS['text_primary'],
                   font=FONTS['normal'])
    style.configure('Title.TLabel',
                   background=COLORS['bg_dark'],
                   foreground=COLORS['text_primary'],
                   font=FONTS['title'])
    style.configure('Subtitle.TLabel',
                   background=COLORS['bg_dark'],
                   foreground=COLORS['text_secondary'],
                   font=FONTS['subtitle'])

    # Button
    style.configure('TButton',
                   background=COLORS['button_bg'],
                   foreground=COLORS['text_primary'],
                   font=FONTS['button'],
                   padding=(10, 5))
    style.map('TButton',
             background=[('active', COLORS['accent_primary']),
                        ('pressed', COLORS['accent_secondary'])])

    # Accent buttons
    style.configure('Accent.TButton',
                   background=COLORS['accent_primary'],
                   foreground=COLORS['text_primary'])
    style.configure('Success.TButton',
                   background=COLORS['accent_success'],
                   foreground=COLORS['text_primary'])
    style.configure('Warning.TButton',
                   background=COLORS['accent_warning'],
                   foreground=COLORS['text_primary'])
    style.configure('Danger.TButton',
                   background=COLORS['accent_danger'],
                   foreground=COLORS['text_primary'])

    # Entry
    style.configure('TEntry',
                   fieldbackground=COLORS['input_bg'],
                   foreground=COLORS['text_primary'],
                   insertcolor=COLORS['text_primary'])

    # Checkbutton
    style.configure('TCheckbutton',
                   background=COLORS['bg_dark'],
                   foreground=COLORS['text_primary'],
                   font=FONTS['normal'])
    style.map('TCheckbutton',
             background=[('active', COLORS['bg_medium'])])

    # Scrollbar
    style.configure('TScrollbar',
                   background=COLORS['bg_medium'],
                   troughcolor=COLORS['bg_dark'],
                   arrowcolor=COLORS['text_secondary'])
    style.map('TScrollbar',
             background=[('active', COLORS['scrollbar'])])

    # Treeview
    style.configure('Treeview',
                   background=COLORS['bg_medium'],
                   foreground=COLORS['text_primary'],
                   fieldbackground=COLORS['bg_medium'],
                   font=FONTS['normal'])
    style.configure('Treeview.Heading',
                   background=COLORS['bg_light'],
                   foreground=COLORS['text_primary'],
                   font=FONTS['subtitle'])
    style.map('Treeview',
             background=[('selected', COLORS['accent_primary'])],
             foreground=[('selected', COLORS['text_primary'])])

    # Notebook (tabs)
    style.configure('TNotebook',
                   background=COLORS['bg_dark'])
    style.configure('TNotebook.Tab',
                   background=COLORS['bg_medium'],
                   foreground=COLORS['text_secondary'],
                   padding=(15, 5))
    style.map('TNotebook.Tab',
             background=[('selected', COLORS['bg_light'])],
             foreground=[('selected', COLORS['text_primary'])])

    # LabelFrame
    style.configure('TLabelframe',
                   background=COLORS['bg_medium'],
                   foreground=COLORS['text_primary'])
    style.configure('TLabelframe.Label',
                   background=COLORS['bg_medium'],
                   foreground=COLORS['accent_secondary'],
                   font=FONTS['subtitle'])

    # Scale (slider)
    style.configure('TScale',
                   background=COLORS['bg_dark'],
                   troughcolor=COLORS['bg_light'])

    # Separator
    style.configure('TSeparator',
                   background=COLORS['border'])

    # PanedWindow
    style.configure('TPanedwindow',
                   background=COLORS['border'])

    return style


def create_styled_button(parent, text, command, style_type='normal', **kwargs):
    """Crea un botón estilizado"""
    colors = {
        'normal': (COLORS['button_bg'], COLORS['text_primary']),
        'accent': (COLORS['accent_primary'], COLORS['text_primary']),
        'success': (COLORS['accent_success'], COLORS['text_primary']),
        'warning': (COLORS['accent_warning'], '#000000'),
        'danger': (COLORS['accent_danger'], COLORS['text_primary']),
    }

    bg, fg = colors.get(style_type, colors['normal'])

    btn = tk.Button(parent,
                   text=text,
                   command=command,
                   bg=bg,
                   fg=fg,
                   activebackground=COLORS['accent_secondary'],
                   activeforeground=COLORS['text_primary'],
                   font=FONTS['button'],
                   relief='flat',
                   cursor='hand2',
                   padx=12,
                   pady=6,
                   **kwargs)

    # Efectos hover
    def on_enter(e):
        if style_type == 'normal':
            btn.config(bg=COLORS['bg_hover'])
        else:
            btn.config(bg=COLORS['accent_secondary'])

    def on_leave(e):
        btn.config(bg=bg)

    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)

    return btn


def create_styled_label(parent, text, style='normal', **kwargs):
    """Crea una etiqueta estilizada"""
    styles = {
        'title': {'font': FONTS['title'], 'fg': COLORS['text_primary']},
        'subtitle': {'font': FONTS['subtitle'], 'fg': COLORS['text_secondary']},
        'normal': {'font': FONTS['normal'], 'fg': COLORS['text_primary']},
        'muted': {'font': FONTS['small'], 'fg': COLORS['text_muted']},
        'accent': {'font': FONTS['normal'], 'fg': COLORS['accent_secondary']},
    }

    style_config = styles.get(style, styles['normal'])

    return tk.Label(parent,
                   text=text,
                   bg=kwargs.pop('bg', COLORS['bg_dark']),
                   **style_config,
                   **kwargs)


def create_styled_entry(parent, **kwargs):
    """Crea un campo de entrada estilizado"""
    entry = tk.Entry(parent,
                    bg=COLORS['input_bg'],
                    fg=COLORS['text_primary'],
                    insertbackground=COLORS['text_primary'],
                    relief='flat',
                    font=FONTS['normal'],
                    highlightthickness=1,
                    highlightbackground=COLORS['border'],
                    highlightcolor=COLORS['accent_primary'],
                    **kwargs)
    return entry


def create_styled_listbox(parent, **kwargs):
    """Crea un listbox estilizado"""
    listbox = tk.Listbox(parent,
                        bg=COLORS['bg_medium'],
                        fg=COLORS['text_primary'],
                        selectbackground=COLORS['accent_primary'],
                        selectforeground=COLORS['text_primary'],
                        relief='flat',
                        font=FONTS['normal'],
                        highlightthickness=1,
                        highlightbackground=COLORS['border'],
                        highlightcolor=COLORS['accent_primary'],
                        **kwargs)
    return listbox


def create_styled_frame(parent, style='dark', **kwargs):
    """Crea un frame estilizado"""
    bg_colors = {
        'dark': COLORS['bg_dark'],
        'medium': COLORS['bg_medium'],
        'light': COLORS['bg_light'],
        'thumbnail': COLORS['thumbnail_bg'],
    }

    return tk.Frame(parent,
                   bg=bg_colors.get(style, COLORS['bg_dark']),
                   **kwargs)


def create_styled_labelframe(parent, text, **kwargs):
    """Crea un LabelFrame estilizado"""
    lf = tk.LabelFrame(parent,
                      text=text,
                      bg=COLORS['bg_medium'],
                      fg=COLORS['accent_secondary'],
                      font=FONTS['subtitle'],
                      relief='flat',
                      bd=1,
                      highlightbackground=COLORS['border'],
                      highlightthickness=1,
                      **kwargs)
    return lf


def create_styled_canvas(parent, **kwargs):
    """Crea un canvas estilizado"""
    return tk.Canvas(parent,
                    bg=COLORS['thumbnail_bg'],
                    highlightthickness=0,
                    **kwargs)


def create_styled_scale(parent, **kwargs):
    """Crea un slider estilizado"""
    return tk.Scale(parent,
                   bg=COLORS['bg_medium'],
                   fg=COLORS['text_primary'],
                   troughcolor=COLORS['bg_light'],
                   activebackground=COLORS['accent_primary'],
                   highlightthickness=0,
                   font=FONTS['small'],
                   **kwargs)


def create_styled_checkbutton(parent, text, variable, command=None, **kwargs):
    """Crea un checkbutton estilizado"""
    cb = tk.Checkbutton(parent,
                       text=text,
                       variable=variable,
                       command=command,
                       bg=COLORS['bg_dark'],
                       fg=COLORS['text_primary'],
                       selectcolor=COLORS['bg_light'],
                       activebackground=COLORS['bg_medium'],
                       activeforeground=COLORS['text_primary'],
                       font=FONTS['normal'],
                       **kwargs)
    return cb


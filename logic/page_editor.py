"""
Módulo para edición de páginas: rotación, redimensionado, márgenes y B/N.
"""
import fitz  # PyMuPDF


class PageEditor:
    """Maneja las operaciones de edición de páginas del PDF"""

    def __init__(self):
        # Almacena las transformaciones pendientes por página
        # Clave: índice de página, Valor: dict con transformaciones
        self.pending_transforms = {}
        # Almacena el estado original de las páginas para preview
        self.original_states = {}

    def save_original_state(self, doc, page_num):
        """Guarda el estado original de una página para comparación"""
        if page_num in self.original_states:
            return  # Ya guardado

        if not doc or page_num < 0 or page_num >= len(doc):
            return

        page = doc[page_num]
        # Renderizar y guardar como imagen original
        render_matrix = fitz.Matrix(0.5, 0.5)  # Escala reducida para preview
        pix = page.get_pixmap(matrix=render_matrix, alpha=False)

        self.original_states[page_num] = {
            'pixmap_bytes': pix.tobytes("png"),
            'width': pix.width,
            'height': pix.height,
            'original_rotation': page.rotation,
            'original_rect': page.rect
        }

    def get_original_pixmap_data(self, page_num):
        """Obtiene los datos del pixmap original de una página"""
        return self.original_states.get(page_num)

    def clear_original_state(self, page_num):
        """Limpia el estado original de una página"""
        if page_num in self.original_states:
            del self.original_states[page_num]

    def rotate_page(self, doc, page_num, direction):
        """
        Rota una página 90 grados.
        direction: 'left' (-90) o 'right' (+90)
        """
        if not doc or page_num < 0 or page_num >= len(doc):
            return False

        # Guardar estado original antes de la primera modificación
        self.save_original_state(doc, page_num)

        page = doc[page_num]
        current_rotation = page.rotation

        if direction == 'left':
            new_rotation = (current_rotation - 90) % 360
        else:  # right
            new_rotation = (current_rotation + 90) % 360

        page.set_rotation(new_rotation)
        return True

    def get_page_rotation(self, doc, page_num):
        """Obtiene la rotación actual de una página"""
        if not doc or page_num < 0 or page_num >= len(doc):
            return 0
        return doc[page_num].rotation

    def set_page_scale(self, page_num, scale):
        """
        Establece la escala pendiente para una página.
        scale: factor de escala (1.0 = 100%, 0.5 = 50%, 2.0 = 200%)
        """
        if page_num not in self.pending_transforms:
            self.pending_transforms[page_num] = {}
        self.pending_transforms[page_num]['scale'] = scale

    def get_page_scale(self, page_num):
        """Obtiene la escala pendiente de una página (1.0 si no hay)"""
        if page_num in self.pending_transforms:
            return self.pending_transforms[page_num].get('scale', 1.0)
        return 1.0

    def clear_page_scale(self, page_num):
        """Elimina la escala pendiente de una página"""
        if page_num in self.pending_transforms:
            if 'scale' in self.pending_transforms[page_num]:
                del self.pending_transforms[page_num]['scale']
            if not self.pending_transforms[page_num]:
                del self.pending_transforms[page_num]

    # =========================================================================
    # MÁRGENES
    # =========================================================================

    def set_page_margins(self, page_num, top=0, right=0, bottom=0, left=0):
        """
        Establece márgenes pendientes para una página.
        Los valores son en puntos (1 punto = 1/72 pulgadas).
        """
        if page_num not in self.pending_transforms:
            self.pending_transforms[page_num] = {}
        self.pending_transforms[page_num]['margins'] = {
            'top': top,
            'right': right,
            'bottom': bottom,
            'left': left
        }

    def set_page_margins_uniform(self, page_num, margin):
        """Establece el mismo margen en todos los lados"""
        self.set_page_margins(page_num, margin, margin, margin, margin)

    def get_page_margins(self, page_num):
        """Obtiene los márgenes pendientes de una página"""
        if page_num in self.pending_transforms:
            return self.pending_transforms[page_num].get('margins',
                {'top': 0, 'right': 0, 'bottom': 0, 'left': 0})
        return {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}

    def clear_page_margins(self, page_num):
        """Elimina los márgenes pendientes de una página"""
        if page_num in self.pending_transforms:
            if 'margins' in self.pending_transforms[page_num]:
                del self.pending_transforms[page_num]['margins']
            if not self.pending_transforms[page_num]:
                del self.pending_transforms[page_num]

    # =========================================================================
    # BLANCO Y NEGRO
    # =========================================================================

    def set_page_grayscale(self, page_num, enabled=True):
        """Establece si una página debe convertirse a blanco y negro"""
        if page_num not in self.pending_transforms:
            self.pending_transforms[page_num] = {}
        self.pending_transforms[page_num]['grayscale'] = enabled

    def get_page_grayscale(self, page_num):
        """Obtiene si una página tiene conversión a B/N pendiente"""
        if page_num in self.pending_transforms:
            return self.pending_transforms[page_num].get('grayscale', False)
        return False

    def clear_page_grayscale(self, page_num):
        """Elimina la conversión B/N pendiente de una página"""
        if page_num in self.pending_transforms:
            if 'grayscale' in self.pending_transforms[page_num]:
                del self.pending_transforms[page_num]['grayscale']
            if not self.pending_transforms[page_num]:
                del self.pending_transforms[page_num]

    # =========================================================================
    # APLICAR TRANSFORMACIONES
    # =========================================================================

    def has_pending_transforms(self):
        """Comprueba si hay transformaciones pendientes"""
        return bool(self.pending_transforms)

    def apply_all_transforms(self, doc):
        """
        Aplica todas las transformaciones pendientes al documento.
        Debe llamarse antes de guardar.
        """
        if not doc:
            return

        # Procesar páginas en orden inverso para no afectar índices
        for page_num in sorted(self.pending_transforms.keys(), reverse=True):
            if page_num >= len(doc):
                continue

            transforms = self.pending_transforms[page_num]

            # Aplicar en orden: primero B/N, luego escala, luego márgenes
            grayscale = transforms.get('grayscale', False)
            scale = transforms.get('scale', 1.0)
            margins = transforms.get('margins', {'top': 0, 'right': 0, 'bottom': 0, 'left': 0})

            has_margins = any(v > 0 for v in margins.values())

            if grayscale or scale != 1.0 or has_margins:
                self._apply_transforms_to_page(doc, page_num, scale, grayscale, margins)

        # Limpiar transformaciones y estados originales después de aplicar
        self.pending_transforms = {}
        self.original_states = {}

    def _apply_transforms_to_page(self, doc, page_num, scale, grayscale, margins):
        """
        Aplica todas las transformaciones a una página.
        """
        page = doc[page_num]
        rect = page.rect

        # Renderizar la página actual como imagen de alta resolución
        render_matrix = fitz.Matrix(3, 3)
        pix = page.get_pixmap(matrix=render_matrix, alpha=False)

        # Aplicar escala de grises si es necesario
        if grayscale:
            # Convertir a escala de grises
            pix = fitz.Pixmap(fitz.csGRAY, pix)
            # Convertir de vuelta a RGB para insertar
            pix = fitz.Pixmap(fitz.csRGB, pix)

        # Convertir pixmap a bytes de imagen PNG
        img_bytes = pix.tobytes("png")

        # Calcular nuevo tamaño con escala
        content_width = rect.width * scale
        content_height = rect.height * scale

        # Calcular tamaño total con márgenes
        total_width = content_width + margins['left'] + margins['right']
        total_height = content_height + margins['top'] + margins['bottom']

        # Crear nuevo rect con el tamaño total
        new_rect = fitz.Rect(0, 0, total_width, total_height)

        # Rect donde irá el contenido (con offset por márgenes)
        content_rect = fitz.Rect(
            margins['left'],
            margins['top'],
            margins['left'] + content_width,
            margins['top'] + content_height
        )

        # Limpiar la página actual
        page.set_mediabox(new_rect)
        page.set_cropbox(new_rect)
        page.clean_contents()

        # Rellenar fondo blanco
        shape = page.new_shape()
        shape.draw_rect(new_rect)
        shape.finish(color=(1, 1, 1), fill=(1, 1, 1))
        shape.commit()

        # Insertar la imagen renderizada en el área de contenido
        page.insert_image(content_rect, stream=img_bytes)

    def get_preview_with_transforms(self, doc, page_num, preview_scale=0.5):
        """
        Genera un preview de la página con las transformaciones aplicadas.
        Retorna bytes PNG de la imagen resultante.
        """
        if not doc or page_num < 0 or page_num >= len(doc):
            return None

        page = doc[page_num]
        transforms = self.pending_transforms.get(page_num, {})

        scale = transforms.get('scale', 1.0)
        grayscale = transforms.get('grayscale', False)
        margins = transforms.get('margins', {'top': 0, 'right': 0, 'bottom': 0, 'left': 0})

        # Renderizar página
        render_matrix = fitz.Matrix(preview_scale, preview_scale)
        pix = page.get_pixmap(matrix=render_matrix, alpha=False)

        # Aplicar escala de grises si es necesario
        if grayscale:
            pix = fitz.Pixmap(fitz.csGRAY, pix)
            pix = fitz.Pixmap(fitz.csRGB, pix)

        return {
            'bytes': pix.tobytes("png"),
            'width': int(pix.width * scale) + int((margins['left'] + margins['right']) * preview_scale),
            'height': int(pix.height * scale) + int((margins['top'] + margins['bottom']) * preview_scale),
            'pix_width': pix.width,
            'pix_height': pix.height
        }

    # =========================================================================
    # UTILIDADES
    # =========================================================================

    def resize_page_to_fit(self, doc, page_num, target_width, target_height):
        """
        Redimensiona una página para que quepa en un tamaño objetivo
        manteniendo la proporción.
        """
        if not doc or page_num < 0 or page_num >= len(doc):
            return False

        page = doc[page_num]
        current_rect = page.rect

        # Calcular escala manteniendo proporción
        scale_w = target_width / current_rect.width
        scale_h = target_height / current_rect.height
        scale = min(scale_w, scale_h)

        self.set_page_scale(page_num, scale)
        return True

    def get_page_size(self, doc, page_num):
        """Retorna el tamaño actual de una página (width, height)"""
        if not doc or page_num < 0 or page_num >= len(doc):
            return (0, 0)

        rect = doc[page_num].rect
        return (rect.width, rect.height)

    def get_scaled_page_size(self, doc, page_num):
        """Retorna el tamaño de la página considerando escala pendiente"""
        width, height = self.get_page_size(doc, page_num)
        scale = self.get_page_scale(page_num)
        return (width * scale, height * scale)

    def get_final_page_size(self, doc, page_num):
        """Retorna el tamaño final incluyendo escala y márgenes"""
        width, height = self.get_scaled_page_size(doc, page_num)
        margins = self.get_page_margins(page_num)
        return (
            width + margins['left'] + margins['right'],
            height + margins['top'] + margins['bottom']
        )

    def has_page_changes(self, doc, page_num):
        """Comprueba si una página tiene cambios pendientes"""
        if page_num not in self.pending_transforms:
            # Verificar si tiene rotación diferente al original
            if page_num in self.original_states:
                original_rot = self.original_states[page_num].get('original_rotation', 0)
                current_rot = self.get_page_rotation(doc, page_num)
                if original_rot != current_rot:
                    return True
            return False
        return True


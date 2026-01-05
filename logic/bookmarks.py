"""
Módulo para manejo de marcadores (TOC - Table of Contents).
"""


class BookmarkManager:
    """Maneja las operaciones de marcadores del PDF"""

    def __init__(self):
        self.toc = []

    def set_toc(self, toc):
        """Establece el TOC actual"""
        self.toc = toc if toc else []

    def get_toc(self):
        """Retorna el TOC actual"""
        return self.toc

    def add_bookmark(self, level, title, page):
        """Añade un nuevo marcador"""
        self.toc.append([level, title, page])
        self.toc.sort(key=lambda x: (x[2], x[0]))  # Ordenar por página y nivel

    def update_bookmark(self, index, level, title, page):
        """Actualiza un marcador existente"""
        if 0 <= index < len(self.toc):
            self.toc[index] = [level, title, page]

    def delete_bookmark(self, index):
        """Elimina un marcador"""
        if 0 <= index < len(self.toc):
            del self.toc[index]

    def get_bookmarks_for_page(self, page):
        """Retorna lista de (índice, marcador) para una página específica"""
        return [(i, b) for i, b in enumerate(self.toc) if b[2] == page]

    def count_bookmarks_for_page(self, page):
        """Cuenta los marcadores en una página"""
        return sum(1 for b in self.toc if b[2] == page)

    def normalize_hierarchy(self, toc=None):
        """
        Normaliza la jerarquía del TOC para que sea válida para PyMuPDF.
        PyMuPDF requiere que los niveles sean consecutivos:
        - El primer nivel debe ser 1
        - Cada nivel siguiente puede ser igual, +1, o menor que el anterior
        - No se puede saltar niveles (ej: de 1 a 3 directamente)
        """
        if toc is None:
            toc = self.toc

        if not toc:
            return toc

        normalized = []
        current_level = 0

        for entry in toc:
            lvl, title, page = entry[0], entry[1], entry[2]

            # El nivel no puede ser mayor que current_level + 1
            if lvl > current_level + 1:
                lvl = current_level + 1

            # El nivel mínimo es 1
            if lvl < 1:
                lvl = 1

            current_level = lvl
            normalized.append([lvl, title, page])

        return normalized

    def prepare_for_display(self, page_order):
        """
        Prepara el TOC para visualización, considerando el orden de páginas.
        Retorna lista de (nivel, título, página_display) normalizada.
        """
        if not self.toc or not page_order:
            return []

        # Crear mapeo de página original -> posición en el orden actual
        page_to_position = {}
        for pos, page_num in enumerate(page_order):
            page_to_position[page_num + 1] = pos + 1  # TOC usa 1-indexed

        # Crear lista de TOC con posiciones actualizadas para ordenar
        toc_with_positions = []
        for i, (lvl, title, page) in enumerate(self.toc):
            display_page = page_to_position.get(page, page)
            toc_with_positions.append((i, lvl, title, page, display_page))

        # Ordenar por posición actual (cómo se verá en el PDF final)
        toc_with_positions.sort(key=lambda x: (x[4], x[1]))

        # Normalizar jerarquía para visualización
        normalized_display = []
        current_level = 0
        for orig_idx, lvl, title, orig_page, display_page in toc_with_positions:
            # Ajustar nivel para que sea válido
            if lvl > current_level + 1:
                lvl = current_level + 1
            if lvl < 1:
                lvl = 1
            current_level = lvl
            normalized_display.append((lvl, title, display_page))

        return normalized_display


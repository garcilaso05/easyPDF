"""
Módulo para manejo del orden de páginas.
"""


class PageOrderManager:
    """Maneja el reordenamiento de páginas del PDF"""

    def __init__(self):
        self.page_order = []

    def initialize(self, num_pages):
        """Inicializa el orden con las páginas del documento"""
        self.page_order = list(range(num_pages))

    def get_order(self):
        """Retorna el orden actual de páginas"""
        return self.page_order

    def set_order(self, order):
        """Establece un orden específico"""
        self.page_order = order

    def extend(self, new_pages):
        """Añade nuevas páginas al final"""
        self.page_order.extend(new_pages)

    def move_up(self, idx):
        """Mueve una página una posición hacia arriba"""
        if idx > 0:
            self.page_order[idx], self.page_order[idx - 1] = \
                self.page_order[idx - 1], self.page_order[idx]
            return True
        return False

    def move_down(self, idx):
        """Mueve una página una posición hacia abajo"""
        if idx < len(self.page_order) - 1:
            self.page_order[idx], self.page_order[idx + 1] = \
                self.page_order[idx + 1], self.page_order[idx]
            return True
        return False

    def has_changes(self):
        """Comprueba si el orden ha cambiado respecto al original"""
        return self.page_order != list(range(len(self.page_order)))

    def apply_reorder(self, doc, toc):
        """
        Aplica el reordenamiento de páginas al documento y actualiza marcadores.
        Retorna el TOC actualizado.
        """
        if not self.has_changes():
            return toc

        # Crear mapeo de página original -> nueva posición
        page_mapping = {}
        for new_pos, old_page in enumerate(self.page_order):
            page_mapping[old_page + 1] = new_pos + 1  # TOC usa 1-indexed

        # Actualizar números de página en el TOC
        new_toc = []
        for lvl, title, old_page in toc:
            if old_page in page_mapping:
                new_toc.append([lvl, title, page_mapping[old_page]])
            else:
                new_toc.append([lvl, title, old_page])

        # Ordenar TOC por nueva página
        new_toc.sort(key=lambda x: (x[2], x[0]))

        # Reordenar las páginas del documento
        doc.select(self.page_order)

        # Resetear orden después de aplicar
        self.page_order = list(range(len(doc)))

        return new_toc

    def get_display_info(self, idx):
        """Retorna información de visualización para una posición"""
        if 0 <= idx < len(self.page_order):
            original_page = self.page_order[idx]
            return {
                'position': idx + 1,
                'original_page': original_page + 1
            }
        return None


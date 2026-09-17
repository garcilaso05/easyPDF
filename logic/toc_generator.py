"""
Módulo para generación de página de índice (TOC) interactiva con hiperenlaces.
"""
import fitz  # PyMuPDF


class TOCGenerator:
    """Genera e inserta páginas de índice (TOC) con hiperenlaces internos y marcado invisible."""

    MARKER_KEY = "EasyPDF_TOC"
    MARKER_VAL = "true"

    @classmethod
    def is_toc_page(cls, doc, page_index=0):
        """Comprueba si una página tiene la marca invisible de índice de easyPDF."""
        if not doc or page_index < 0 or page_index >= len(doc):
            return False
        try:
            page = doc[page_index]
            val = doc.xref_get_key(page.xref, cls.MARKER_KEY)
            return val and val[0] == "bool" and val[1] == cls.MARKER_VAL
        except Exception:
            return False

    @classmethod
    def clean_toc_pages(cls, doc):
        """
        Elimina las páginas iniciales marcadas como índice de easyPDF.
        Retorna la cantidad de páginas de índice eliminadas.
        """
        if not doc:
            return 0

        removed_count = 0
        while len(doc) > 0 and cls.is_toc_page(doc, 0):
            doc.delete_page(0)
            removed_count += 1

        return removed_count

    @classmethod
    def clean_doc_and_toc(cls, doc):
        """
        Detecta y elimina las páginas de índice generadas por easyPDF
        y ajusta el TOC limpiando entradas huérfanas.
        Retorna: (doc, clean_toc, removed_count)
        """
        if not doc:
            return doc, [], 0

        removed_count = cls.clean_toc_pages(doc)
        if removed_count == 0:
            return doc, doc.get_toc(), 0

        # PyMuPDF actualiza automáticamente los destinos de marcadores al eliminar páginas.
        # Filtramos marcadores que apuntaban a las páginas de índice eliminadas (página <= 0).
        raw_toc = doc.get_toc()
        clean_toc = [entry for entry in raw_toc if entry[2] > 0]

        try:
            doc.set_toc(clean_toc)
        except Exception:
            pass

        return doc, clean_toc, removed_count

    @classmethod
    def generate_toc_pages(cls, doc, toc, title="Índice", subtitle=""):
        """
        Genera e inserta páginas de índice al principio del documento (página 0..N-1).
        - doc: documento PyMuPDF
        - toc: lista de marcadores [[level, title, page_1_indexed], ...]
        - title: texto para el título superior
        - subtitle: texto para el subtítulo (opcional)

        Retorna: cantidad de páginas de índice añadidas (int).
        """
        if not doc or not toc:
            return 0

        # Obtener dimensiones base del documento o usar A4 estándar (595 x 842 pt)
        if len(doc) > 0:
            first_rect = doc[0].rect
            page_width = first_rect.width
            page_height = first_rect.height
        else:
            page_width = 595.0
            page_height = 842.0

        margin_left = 54.0   # 0.75 pulgadas
        margin_right = 54.0
        margin_top = 58.0
        margin_bottom = 54.0
        usable_width = page_width - margin_left - margin_right

        line_height = 21.0
        indent_step = 18.0

        # Espacio inicial de cabecera en la primera página
        header_height_p1 = 28.0  # Título
        if subtitle.strip():
            header_height_p1 += 20.0  # Subtítulo
        header_height_p1 += 25.0  # Espacio + línea separadora + margen inferior

        available_h_p1 = page_height - margin_top - header_height_p1 - margin_bottom
        entries_p1 = max(1, int(available_h_p1 // line_height))

        # Espacio de cabecera en páginas subsiguientes
        header_height_subseq = 35.0
        available_h_subseq = page_height - margin_top - header_height_subseq - margin_bottom
        entries_subseq = max(1, int(available_h_subseq // line_height))

        # Calcular cuántas páginas de índice se necesitan
        total_entries = len(toc)
        if total_entries <= entries_p1:
            num_pages = 1
        else:
            remaining = total_entries - entries_p1
            num_pages = 1 + (remaining + entries_subseq - 1) // entries_subseq

        # Distribuir entradas por página
        pages_entries = []
        p1_items = toc[:entries_p1]
        pages_entries.append(p1_items)
        curr_idx = entries_p1
        while curr_idx < total_entries:
            pages_entries.append(toc[curr_idx:curr_idx + entries_subseq])
            curr_idx += entries_subseq

        # Crear e insertar las páginas de índice al principio
        for p_idx in range(num_pages):
            page = doc.new_page(pno=p_idx, width=page_width, height=page_height)
            # Marcar de forma invisible en el diccionario PDF
            doc.xref_set_key(page.xref, cls.MARKER_KEY, cls.MARKER_VAL)

        # Dibujar contenido en cada página de índice
        for page_i, entries in enumerate(pages_entries):
            page = doc[page_i]
            y = margin_top

            if page_i == 0:
                # Título principal pegado arriba a la izquierda
                title_text = title.strip() if title.strip() else "Índice"
                page.insert_text(
                    (margin_left, y + 20),
                    title_text,
                    fontname="hebo",
                    fontsize=22,
                    color=(0.10, 0.10, 0.15)
                )
                y += 26

                # Subtítulo justo debajo
                if subtitle.strip():
                    page.insert_text(
                        (margin_left, y + 10),
                        subtitle.strip(),
                        fontname="helv",
                        fontsize=11,
                        color=(0.35, 0.35, 0.40)
                    )
                    y += 18

                # Línea separadora sutil
                shape = page.new_shape()
                shape.draw_line(fitz.Point(margin_left, y + 8), fitz.Point(page_width - margin_right, y + 8))
                shape.finish(color=(0.80, 0.82, 0.85), width=0.8)
                shape.commit()
                y += 24
            else:
                # Cabecera de continuación para páginas subsiguientes
                cont_title = f"{title.strip() if title.strip() else 'Índice'} (cont.)"
                page.insert_text(
                    (margin_left, y + 14),
                    cont_title,
                    fontname="hebo",
                    fontsize=14,
                    color=(0.20, 0.20, 0.25)
                )
                shape = page.new_shape()
                shape.draw_line(fitz.Point(margin_left, y + 22), fitz.Point(page_width - margin_right, y + 22))
                shape.finish(color=(0.85, 0.86, 0.88), width=0.6)
                shape.commit()
                y += 34

            # Dibujar entradas de marcadores con sangría e hiperenlaces
            for lvl, entry_title, orig_page in entries:
                # Nivel de sangría: tabulador a la izquierda
                indent = (lvl - 1) * indent_step
                text_x = margin_left + indent

                # Página real de destino en el documento final (desplazada por num_pages)
                target_page_1_indexed = orig_page + num_pages
                target_page_0_indexed = target_page_1_indexed - 1
                page_str = str(target_page_1_indexed)

                is_main = (lvl == 1)
                font_name = "hebo" if is_main else "helv"
                font_size = 11 if is_main else 10
                text_color = (0.10, 0.10, 0.15) if is_main else (0.25, 0.25, 0.30)

                # Ancho del texto y del número de página
                title_w = fitz.get_text_length(entry_title, fontname=font_name, fontsize=font_size)
                page_w = fitz.get_text_length(page_str, fontname="helv", fontsize=font_size)

                # Truncar título con elipsis si es excesivamente largo para no solaparse con el número de página
                max_title_w = usable_width - indent - page_w - 24
                display_entry_title = entry_title
                if title_w > max_title_w and max_title_w > 50:
                    while title_w > max_title_w and len(display_entry_title) > 5:
                        display_entry_title = display_entry_title[:-4] + "..."
                        title_w = fitz.get_text_length(display_entry_title, fontname=font_name, fontsize=font_size)

                # Dibujar título del marcador
                page.insert_text(
                    (text_x, y),
                    display_entry_title,
                    fontname=font_name,
                    fontsize=font_size,
                    color=text_color
                )

                # Dibujar número de página alineado a la derecha
                num_x = page_width - margin_right - page_w
                page.insert_text(
                    (num_x, y),
                    page_str,
                    fontname="helv",
                    fontsize=font_size,
                    color=text_color
                )

                # Puntos de guía (dot leaders)
                dots_start = text_x + title_w + 6
                dots_end = num_x - 6
                if dots_end > dots_start + 12:
                    dot_count = int((dots_end - dots_start) / 7.0)
                    dots_text = ". " * dot_count
                    page.insert_text(
                        (dots_start, y),
                        dots_text,
                        fontname="helv",
                        fontsize=8.5,
                        color=(0.70, 0.72, 0.76)
                    )

                # Hiperenlace interactivo en toda la línea del marcador
                link_rect = fitz.Rect(margin_left, y - font_size - 2, page_width - margin_right, y + 4)
                page.insert_link({
                    "kind": fitz.LINK_GOTO,
                    "from": link_rect,
                    "page": target_page_0_indexed
                })

                y += line_height

        return num_pages

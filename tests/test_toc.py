"""
Pruebas unitarias para la funcionalidad de Índice (TOC) interactivo y marcado invisible.
"""
import os
import tempfile
import unittest
import fitz

from logic.toc_generator import TOCGenerator
from logic.pdf_handler import PDFHandler


class TestTOCGenerator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_sample_doc(self, num_pages=5):
        """Crea un documento de prueba con N páginas."""
        doc = fitz.open()
        for i in range(1, num_pages + 1):
            p = doc.new_page(width=595, height=842)
            p.insert_text((72, 100), f"Página real {i}")
        # Asegurar serialización
        return fitz.open("pdf", doc.tobytes())

    def test_single_page_toc_generation(self):
        """Verifica la creación de índice de una sola página con hiperenlaces y marca invisible."""
        doc = self._create_sample_doc(5)
        toc = [
            [1, "Capítulo 1: Introducción", 1],
            [2, "Sección 1.1: Contexto", 2],
            [2, "Sección 1.2: Metodología", 3],
            [1, "Capítulo 2: Resultados", 4],
            [1, "Capítulo 3: Conclusiones", 5],
        ]
        doc.set_toc(toc)

        added = TOCGenerator.generate_toc_pages(
            doc, toc, title="Índice Principal", subtitle="Documento de Prueba"
        )
        self.assertEqual(added, 1)
        self.assertEqual(len(doc), 6)

        # Comprobar marca invisible en página 0
        self.assertTrue(TOCGenerator.is_toc_page(doc, 0))
        self.assertFalse(TOCGenerator.is_toc_page(doc, 1))

        # Guardar para verificar persistencia de hiperenlaces
        out_path = os.path.join(self.temp_dir, "test_toc.pdf")
        doc.save(out_path)
        doc.close()

        # Reabrir y verificar enlaces en la página 0
        doc_saved = fitz.open(out_path)
        p0 = doc_saved[0]
        links = p0.get_links()
        self.assertEqual(len(links), 5)

        # Los enlaces deben apuntar a las páginas 0-indexadas desplazadas (1, 2, 3, 4, 5)
        expected_dest_pages = [1, 2, 3, 4, 5]
        actual_dest_pages = [lnk["page"] for lnk in links]
        self.assertEqual(actual_dest_pages, expected_dest_pages)

        # Comprobar que todos los enlaces son internos (kind == LINK_GOTO == 1)
        for lnk in links:
            self.assertEqual(lnk["kind"], fitz.LINK_GOTO)

        doc_saved.close()

    def test_multi_page_toc_generation(self):
        """Verifica que un número grande de marcadores genera múltiples páginas de índice."""
        doc = self._create_sample_doc(50)
        # Generar 60 marcadores para forzar paginación del índice
        toc = []
        for i in range(1, 61):
            lvl = 1 if i % 4 == 1 else (2 if i % 4 in (2, 3) else 3)
            target_page = min(50, (i + 1) // 2)
            toc.append([lvl, f"Marcador número {i:02d} - Título de sección", target_page])

        doc.set_toc(toc)
        added = TOCGenerator.generate_toc_pages(doc, toc, title="Índice Extenso")

        # Debe generar 2 o más páginas de índice
        self.assertGreaterEqual(added, 2)

        # Cada una de las páginas generadas debe tener la marca invisible
        for p_idx in range(added):
            self.assertTrue(TOCGenerator.is_toc_page(doc, p_idx))
        # La primera página real no debe tener la marca
        self.assertFalse(TOCGenerator.is_toc_page(doc, added))

        doc.close()

    def test_clean_doc_and_toc_roundtrip(self):
        """Verifica que al limpiar las páginas de índice, el documento y el TOC vuelven a su estado original."""
        doc = self._create_sample_doc(4)
        orig_toc = [
            [1, "Parte 1", 1],
            [2, "Subsección", 2],
            [1, "Parte 2", 3],
        ]
        doc.set_toc(orig_toc)

        # Añadir índice
        added = TOCGenerator.generate_toc_pages(doc, orig_toc, title="Índice")
        shifted_toc = [[lvl, t, p + added] for lvl, t, p in orig_toc]
        doc.set_toc(shifted_toc)

        out_path = os.path.join(self.temp_dir, "roundtrip.pdf")
        doc.save(out_path)
        doc.close()

        # Reabrir el archivo simulando easyPDF load
        doc_reopened = fitz.open(out_path)
        self.assertEqual(len(doc_reopened), 5)  # 1 índice + 4 páginas reales

        cleaned_doc, clean_toc, removed = TOCGenerator.clean_doc_and_toc(doc_reopened)
        self.assertEqual(removed, 1)
        self.assertEqual(len(cleaned_doc), 4)
        self.assertEqual(clean_toc, orig_toc)

        cleaned_doc.close()

    def test_pdf_handler_save_with_toc_and_in_memory_restoration(self):
        """Verifica que PDFHandler.save añade el índice en el archivo pero restaura el documento en memoria."""
        handler = PDFHandler()
        doc = self._create_sample_doc(3)
        toc = [
            [1, "Capítulo 1", 1],
            [1, "Capítulo 2", 2],
            [1, "Capítulo 3", 3],
        ]

        out_path = os.path.join(self.temp_dir, "handler_save_test.pdf")

        # Mocking filedialog.asksaveasfilename para que devuelva out_path
        from unittest.mock import patch
        with patch("tkinter.filedialog.asksaveasfilename", return_value=out_path), \
             patch("tkinter.messagebox.showinfo"):
            success = handler.save(doc, toc, toc_options={
                "include_toc": True,
                "title": "Índice de Prueba",
                "subtitle": "Subtítulo de Prueba"
            })

        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_path))

        # En memoria, el doc debe mantener su longitud original (3 páginas)
        self.assertEqual(len(doc), 3)

        # En disco, el PDF guardado debe tener 4 páginas (página 0 de índice + 3)
        saved_doc = fitz.open(out_path)
        self.assertEqual(len(saved_doc), 4)
        self.assertTrue(TOCGenerator.is_toc_page(saved_doc, 0))

        # Verificar hiperenlaces del archivo guardado
        links = saved_doc[0].get_links()
        self.assertEqual(len(links), 3)
        self.assertEqual([l["page"] for l in links], [1, 2, 3])

        saved_doc.close()
        doc.close()

    def test_pdf_handler_save_without_toc(self):
        """Verifica que si include_toc es False, no se añade ninguna página 0."""
        handler = PDFHandler()
        doc = self._create_sample_doc(3)
        toc = [[1, "Capítulo 1", 1]]

        out_path = os.path.join(self.temp_dir, "handler_no_toc.pdf")

        from unittest.mock import patch
        with patch("tkinter.filedialog.asksaveasfilename", return_value=out_path), \
             patch("tkinter.messagebox.showinfo"):
            success = handler.save(doc, toc, toc_options={"include_toc": False})

        self.assertTrue(success)
        saved_doc = fitz.open(out_path)
        self.assertEqual(len(saved_doc), 3)
        self.assertFalse(TOCGenerator.is_toc_page(saved_doc, 0))

        saved_doc.close()
        doc.close()

    def test_pdf_handler_load_strips_toc(self):
        """Verifica que PDFHandler.load() descarta la página de índice y restaura el TOC original."""
        handler = PDFHandler()
        doc = self._create_sample_doc(4)
        orig_toc = [
            [1, "Sección Inicial", 1],
            [2, "Detalle Técnico", 2],
            [1, "Sección Final", 4],
        ]

        out_path = os.path.join(self.temp_dir, "to_reload.pdf")
        from unittest.mock import patch
        with patch("tkinter.filedialog.asksaveasfilename", return_value=out_path), \
             patch("tkinter.messagebox.showinfo"):
            handler.save(doc, orig_toc, toc_options={"include_toc": True, "title": "Mi Índice"})

        # Ahora cargamos usando PDFHandler.load()
        with patch("tkinter.filedialog.askopenfilename", return_value=out_path):
            loaded_doc, loaded_toc = handler.load()

        self.assertIsNotNone(loaded_doc)
        # Debe tener 4 páginas (la página de índice fue descartada)
        self.assertEqual(len(loaded_doc), 4)
        self.assertFalse(TOCGenerator.is_toc_page(loaded_doc, 0))
        self.assertEqual(loaded_toc, orig_toc)

        loaded_doc.close()
        doc.close()

    def test_pdf_handler_merge_strips_toc(self):
        """Verifica que merge_single descarta páginas de índice de PDFs fusionados."""
        handler = PDFHandler()
        # PDF base
        base_doc = self._create_sample_doc(2)
        base_toc = [[1, "Base Doc P1", 1]]
        base_order = [0, 1]

        # PDF a fusionar (guardado con índice)
        doc_to_merge = self._create_sample_doc(2)
        merge_toc = [[1, "Merge P1", 1], [1, "Merge P2", 2]]
        merge_path = os.path.join(self.temp_dir, "doc_to_merge.pdf")

        from unittest.mock import patch
        with patch("tkinter.filedialog.asksaveasfilename", return_value=merge_path), \
             patch("tkinter.messagebox.showinfo"):
            handler.save(doc_to_merge, merge_toc, toc_options={"include_toc": True})
        doc_to_merge.close()

        # Fusionar
        merged_doc, merged_toc, merged_order = handler.merge_single(
            base_doc, base_toc, base_order, merge_path
        )

        # Base tenía 2 páginas, el doc a fusionar tenía 2 páginas reales (+1 de índice que debe ser descartada)
        # Total debe ser 4 páginas
        self.assertEqual(len(merged_doc), 4)
        self.assertEqual(len(merged_order), 4)
        # Los marcadores de merge_toc deben sumarse con offset de 2 páginas
        self.assertEqual(merged_toc[0], [1, "Base Doc P1", 1])
        self.assertEqual(merged_toc[1], [1, "Merge P1", 3])
        self.assertEqual(merged_toc[2], [1, "Merge P2", 4])

        merged_doc.close()

    def test_special_characters_and_spanish_accents(self):
        """Verifica el soporte adecuado de caracteres especiales y tildes en español."""
        doc = self._create_sample_doc(3)
        toc = [
            [1, "1. Introducción y Metodología Española", 1],
            [2, "1.1. Análisis de Diseño & Maquetación (Pág. 2)", 2],
            [1, "2. Conclusiones: ¡Éxito y Añadidos!", 3],
        ]
        doc.set_toc(toc)

        added = TOCGenerator.generate_toc_pages(
            doc, toc,
            title="Índice General con Tildes: áéíóú ñ",
            subtitle="Subtítulo: ¿Preguntas y Respuestas? — Versión 2.0"
        )
        self.assertEqual(added, 1)

        out_path = os.path.join(self.temp_dir, "accents_test.pdf")
        doc.save(out_path)
        doc.close()

        # Verificar que el PDF se abre y los hiperenlaces existen
        doc_saved = fitz.open(out_path)
        self.assertEqual(len(doc_saved[0].get_links()), 3)
        doc_saved.close()


if __name__ == "__main__":
    unittest.main()


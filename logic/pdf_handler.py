"""
Módulo para manejo de archivos PDF: carga, guardado y fusión.
"""
import os
import subprocess
import tempfile
import fitz  # PyMuPDF
from tkinter import filedialog, messagebox


class PDFHandler:
    """Maneja las operaciones de archivos PDF"""

    def __init__(self):
        self.doc = None

    def load(self):
        """Carga un archivo PDF y retorna el documento y su TOC"""
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not path:
            return None, None

        self.doc = fitz.open(path)
        toc = self.doc.get_toc()
        return self.doc, toc

    def merge(self, current_doc, current_toc, current_page_order):
        """
        Fusiona otro PDF con el actual (método legacy).
        Retorna: (doc, toc, page_order) actualizados o None si se cancela
        """
        path = filedialog.askopenfilename(
            title="Selecciona PDF para fusionar",
            filetypes=[("PDF", "*.pdf")]
        )
        if not path:
            return None

        return self.merge_single(current_doc, current_toc, current_page_order, path)

    def merge_single(self, current_doc, current_toc, current_page_order, path):
        """
        Fusiona un solo PDF dado su path.
        Retorna: (doc, toc, page_order) actualizados o None si falla
        """
        try:
            new_doc = fitz.open(path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el PDF:\n{e}")
            return None

        if not current_doc:
            # Si no hay documento cargado, este se convierte en el principal
            self.doc = new_doc
            toc = new_doc.get_toc()
            page_order = list(range(len(new_doc)))
            return self.doc, toc, page_order

        # Fusionar: añadir páginas del nuevo documento
        current_page_count = len(current_doc)

        # Obtener TOC del nuevo documento y ajustar números de página
        new_toc = new_doc.get_toc()
        for entry in new_toc:
            entry[2] += current_page_count
            current_toc.append(entry)

        # Insertar todas las páginas del nuevo documento
        current_doc.insert_pdf(new_doc)

        # Actualizar el orden de páginas
        new_pages = list(range(current_page_count, len(current_doc)))
        current_page_order.extend(new_pages)

        new_doc.close()

        return current_doc, current_toc, current_page_order

    def add_images_as_pages(self, current_doc, current_page_order, image_paths):
        """
        Añade imágenes como nuevas páginas al PDF.
        Retorna: (doc, page_order, added_count) o None si falla
        """
        if not image_paths:
            return None

        # Si no hay documento, crear uno nuevo
        if not current_doc:
            current_doc = fitz.open()
            self.doc = current_doc
            current_page_order = []

        added_count = 0

        for img_path in image_paths:
            try:
                # Abrir la imagen con PyMuPDF
                img_doc = fitz.open(img_path)

                # Convertir imagen a PDF
                # PyMuPDF puede manejar imágenes directamente
                pdf_bytes = img_doc.convert_to_pdf()
                img_doc.close()

                # Abrir los bytes como documento PDF
                img_pdf = fitz.open("pdf", pdf_bytes)

                # Obtener tamaño de página actual
                current_page_count = len(current_doc)

                # Insertar la página de imagen
                current_doc.insert_pdf(img_pdf)

                img_pdf.close()

                # Actualizar orden de páginas
                new_pages = list(range(current_page_count, len(current_doc)))
                current_page_order.extend(new_pages)

                added_count += 1

            except Exception as e:
                messagebox.showwarning("Aviso", f"No se pudo añadir la imagen:\n{img_path}\n\nError: {e}")
                continue

        if added_count > 0:
            return current_doc, current_page_order, added_count

        return None

    def save(self, doc, toc):
        """Guarda el PDF con el TOC actualizado"""
        if not doc:
            messagebox.showwarning("Aviso", "No hay ningún PDF cargado")
            return False

        try:
            doc.set_toc(toc)
        except ValueError as e:
            messagebox.showerror("Error", f"Error en la jerarquía de marcadores:\n{e}")
            return False

        out = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if out:
            doc.save(out)
            messagebox.showinfo("OK", "PDF guardado correctamente")
            return True
        return False

    def get_page_pixmap(self, doc, page_num, scale=1.0):
        """Obtiene el pixmap de una página con escala"""
        if not doc or page_num < 0 or page_num >= len(doc):
            return None

        page = doc[page_num]
        mat = fitz.Matrix(scale, scale)
        return page.get_pixmap(matrix=mat)

    def get_page_rect(self, doc, page_num):
        """Obtiene el rectángulo de una página"""
        if not doc or page_num < 0 or page_num >= len(doc):
            return None
        return doc[page_num].rect

    def add_documents_as_pages(self, current_doc, current_toc, current_page_order, doc_paths):
        """
        Convierte documentos Word/ODT a PDF y los añade como páginas.
        Soporta: .doc, .docx, .odt, .rtf
        Retorna: (doc, toc, page_order, added_count) o None si falla
        """
        if not doc_paths:
            return None

        # Si no hay documento, crear uno nuevo
        if not current_doc:
            current_doc = fitz.open()
            self.doc = current_doc
            current_page_order = []
            current_toc = []

        added_count = 0

        for doc_path in doc_paths:
            try:
                # Convertir documento a PDF
                pdf_path = self._convert_document_to_pdf(doc_path)

                if pdf_path and os.path.exists(pdf_path):
                    # Abrir el PDF convertido
                    converted_doc = fitz.open(pdf_path)

                    # Obtener tamaño de página actual
                    current_page_count = len(current_doc)

                    # Obtener TOC del documento convertido
                    new_toc = converted_doc.get_toc()
                    for entry in new_toc:
                        entry[2] += current_page_count
                        current_toc.append(entry)

                    # Insertar las páginas
                    current_doc.insert_pdf(converted_doc)

                    converted_doc.close()

                    # Eliminar archivo temporal
                    try:
                        os.remove(pdf_path)
                    except:
                        pass

                    # Actualizar orden de páginas
                    new_pages = list(range(current_page_count, len(current_doc)))
                    current_page_order.extend(new_pages)

                    added_count += 1
                else:
                    messagebox.showwarning("Aviso", f"No se pudo convertir:\n{doc_path}")

            except Exception as e:
                messagebox.showwarning("Aviso", f"Error al procesar:\n{doc_path}\n\n{e}")
                continue

        if added_count > 0:
            return current_doc, current_toc, current_page_order, added_count

        return None

    def _convert_document_to_pdf(self, doc_path):
        """
        Convierte un documento Word/ODT a PDF.
        Intenta usar LibreOffice (soffice) que está disponible en la mayoría de sistemas.
        """
        # Crear directorio temporal para el PDF de salida
        temp_dir = tempfile.mkdtemp()

        # Intentar con LibreOffice primero (funciona con todos los formatos)
        pdf_path = self._convert_with_libreoffice(doc_path, temp_dir)
        if pdf_path:
            return pdf_path

        # Intentar con docx2pdf (solo Windows, solo .docx)
        if doc_path.lower().endswith(('.docx', '.doc')):
            pdf_path = self._convert_with_docx2pdf(doc_path, temp_dir)
            if pdf_path:
                return pdf_path

        # Intentar con comtypes (Windows con Word instalado)
        if doc_path.lower().endswith(('.docx', '.doc')):
            pdf_path = self._convert_with_word_com(doc_path, temp_dir)
            if pdf_path:
                return pdf_path

        return None

    def _convert_with_libreoffice(self, doc_path, output_dir):
        """Convierte usando LibreOffice en modo headless"""
        # Posibles ubicaciones de LibreOffice
        soffice_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            "soffice",  # Si está en PATH
            "/usr/bin/soffice",  # Linux
            "/usr/bin/libreoffice",  # Linux alternativo
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
        ]

        soffice_exe = None
        for path in soffice_paths:
            if os.path.exists(path) or path in ("soffice", "libreoffice"):
                soffice_exe = path
                break

        if not soffice_exe:
            return None

        try:
            # Ejecutar LibreOffice en modo headless
            cmd = [
                soffice_exe,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", output_dir,
                doc_path
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            # Buscar el PDF generado
            base_name = os.path.splitext(os.path.basename(doc_path))[0]
            pdf_path = os.path.join(output_dir, base_name + ".pdf")

            if os.path.exists(pdf_path):
                return pdf_path

        except Exception:
            pass

        return None

    def _convert_with_docx2pdf(self, doc_path, output_dir):
        """Convierte usando docx2pdf (requiere Microsoft Word en Windows)"""
        try:
            from docx2pdf import convert

            base_name = os.path.splitext(os.path.basename(doc_path))[0]
            pdf_path = os.path.join(output_dir, base_name + ".pdf")

            convert(doc_path, pdf_path)

            if os.path.exists(pdf_path):
                return pdf_path

        except ImportError:
            pass  # docx2pdf no está instalado
        except Exception:
            pass

        return None

    def _convert_with_word_com(self, doc_path, output_dir):
        """Convierte usando COM de Microsoft Word (solo Windows)"""
        if os.name != 'nt':
            return None

        try:
            import comtypes.client

            word = comtypes.client.CreateObject('Word.Application')
            word.Visible = False

            doc = word.Documents.Open(doc_path)

            base_name = os.path.splitext(os.path.basename(doc_path))[0]
            pdf_path = os.path.join(output_dir, base_name + ".pdf")

            # 17 = wdFormatPDF
            doc.SaveAs(pdf_path, FileFormat=17)
            doc.Close()
            word.Quit()

            if os.path.exists(pdf_path):
                return pdf_path

        except ImportError:
            pass  # comtypes no está instalado
        except Exception:
            pass

        return None


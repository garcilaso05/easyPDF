"""
PDF Bookmark Editor - Punto de entrada principal.

Aplicación para editar marcadores de PDFs, reordenar páginas y fusionar documentos.
"""
import tkinter as tk
from ui.app import PDFEditorApp


def main():
    root = tk.Tk()
    root.geometry("950x600")
    app = PDFEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


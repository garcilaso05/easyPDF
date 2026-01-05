# 📄 easyPDF

**easyPDF** es una aplicación de escritorio profesional para edición de PDFs que agrupa múltiples funcionalidades de herramientas como iLovePDF en un solo programa, **sin límites** y sin necesidad de descargar el PDF para cambiar de herramienta.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## ✨ Características Principales

### 📑 Gestión de PDFs
- **Cargar y guardar** documentos PDF
- **Fusionar múltiples PDFs** en un solo documento
- **Añadir imágenes** (JPG, PNG, etc.) como nuevas páginas
- **Importar documentos** de otros formatos

### 🔖 Marcadores (Bookmarks)
- Crear, editar y eliminar marcadores
- Jerarquía multinivel con sangría visual
- Visualización de marcadores por página
- Normalización automática de jerarquías

### 🔀 Reordenamiento de Páginas
- Modo interactivo para reordenar páginas
- Vista de miniaturas (thumbnails)
- Mover páginas arriba/abajo
- Previsualización en tiempo real

### ✏️ Edición de Páginas
- **Rotar páginas** 90° a la izquierda o derecha
- **Redimensionar páginas** con escala personalizada
- **Ajustar márgenes** (superior, inferior, izquierdo, derecho)
- **Convertir a blanco y negro** (escala de grises)
- Vista previa lado a lado (original vs. resultado)

### 🎨 Interfaz Profesional
- Tema oscuro moderno
- Distribución en 3 paneles:
  - **Panel izquierdo**: Lista de páginas con miniaturas
  - **Panel central**: Previsualización de página
  - **Panel derecho**: Gestión de marcadores y herramientas de edición
- Controles intuitivos con iconos
- Zoom en previsualización

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Dependencias
Instala las dependencias necesarias:

```bash
pip install PyMuPDF pillow
```

O si tienes un archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Dependencias principales:
- **PyMuPDF (fitz)**: Para manipulación de PDFs
- **Pillow (PIL)**: Para procesamiento de imágenes
- **tkinter**: Para la interfaz gráfica (incluido en Python estándar)

## 💻 Uso

### Iniciar la Aplicación

```bash
python main.py
```

### Flujo de Trabajo Básico

1. **Cargar un PDF**
   - Haz clic en `📂 Cargar` para abrir un documento PDF
   - Las páginas se mostrarán como miniaturas en el panel izquierdo

2. **Editar Marcadores**
   - Selecciona una página del panel izquierdo
   - En el panel derecho, gestiona los marcadores:
     - Añadir nuevo marcador
     - Editar marcadores existentes
     - Eliminar marcadores
     - Ajustar niveles de jerarquía

3. **Reordenar Páginas**
   - Activa el modo `🔀 Ordenar`
   - Selecciona páginas y usa los botones ⬆️ / ⬇️ para moverlas
   - Desactiva el modo para aplicar los cambios

4. **Editar Páginas Individuales**
   - Activa el modo `✏️ Editar`
   - Selecciona una página
   - Aplica transformaciones:
     - Rotar con botones ↪️ / ↩️
     - Escalar (25% a 200%)
     - Ajustar márgenes
     - Convertir a B/N
   - Previsualiza los cambios antes de aplicarlos

5. **Fusionar Contenido**
   - `📑 PDFs`: Añadir otros documentos PDF
   - `🖼️ Imágenes`: Insertar imágenes como páginas
   - `📝 Docs`: Importar documentos de otros formatos

6. **Guardar el Resultado**
   - Haz clic en `💾 Guardar`
   - Elige la ubicación y nombre del archivo
   - Todos los cambios se aplicarán al guardar

## 📁 Estructura del Proyecto

```
easyPDF/
├── main.py                 # Punto de entrada de la aplicación
├── README.md              # Este archivo
├── LICENSE                # Licencia del proyecto
├── logic/                 # Lógica de negocio
│   ├── __init__.py
│   ├── bookmarks.py       # Gestión de marcadores
│   ├── page_editor.py     # Edición de páginas (rotar, escalar, etc.)
│   ├── page_order.py      # Reordenamiento de páginas
│   └── pdf_handler.py     # Manejo de archivos PDF
└── ui/                    # Interfaz de usuario
    ├── __init__.py
    ├── app.py             # Clase principal de la aplicación
    ├── panels.py          # Construcción de paneles UI
    └── styles.py          # Tema y estilos visuales
```

## 🛠️ Tecnologías Utilizadas

- **Python**: Lenguaje de programación principal
- **Tkinter**: Framework para interfaz gráfica (GUI)
- **PyMuPDF (fitz)**: Librería para manipulación de PDFs
- **Pillow (PIL)**: Procesamiento y manipulación de imágenes

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar easyPDF:

1. Haz un fork del proyecto
2. Crea una rama para tu característica (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 📧 Contacto

Para reportar bugs, sugerencias o preguntas, abre un issue en el repositorio del proyecto.

## 🎯 Roadmap / Futuras Características

- [ ] Extracción de páginas
- [ ] Dividir PDF en múltiples archivos
- [ ] Añadir marcas de agua
- [ ] Protección con contraseña
- [ ] Compresión de PDFs
- [ ] OCR (reconocimiento de texto)
- [ ] Firma digital

---

**Desarrollado con ❤️ para simplificar el trabajo con PDFs**

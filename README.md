# 🧠 Multi-Agent System for Campaign Analysis

Este proyecto implementa un sistema multiagente para analizar campañas publicitarias de compañías energéticas y generar informes detallados en formato Markdown y PDF. Utiliza inteligencia artificial y herramientas avanzadas para buscar, procesar y estructurar la información.

---

## 🚀 Características
- **Análisis de Consultas**: Interpreta solicitudes de los usuarios y define los pasos para la recopilación de datos.
- **Scraping Web**: Extrae datos de páginas web, incluyendo contenido dinámico y texto en imágenes mediante OCR.
- **Resumen de Campañas**: Organiza y resume datos de campañas publicitarias en un formato estructurado.
- **Cálculo de Precios**: Calcula estimaciones de costos anuales para clientes promedio.
- **Generación de Informes**: Compila la información en un informe en Markdown, que luego puede ser convertido a PDF.

---

## 📂 Estructura del Proyecto
```plaintext
.
├── agents/
│   ├── agents.yaml       # Configuración de los agentes
│   ├── tasks.yaml        # Configuración de las tareas
├── main.py               # Código principal del proyecto
├── informe.md            # Informe generado en formato Markdown
├── output.pdf            # Informe convertido a PDF
└── README.md             # Este archivo
```

## 🛠️ Requisitos

### Software
- **Python**: Versión 3.9 o superior.
- **Tesseract OCR**: Para extracción de texto de imágenes. Asegúrate de que está instalado y accesible desde la línea de comandos.
- **Playwright**: Para scraping de contenido dinámico generado con JavaScript.

### Librerías Python
Instala las dependencias necesarias ejecutando:
```bash
pip install -r requirements.txt
```
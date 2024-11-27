import os
import json
import yaml
from crewai import Agent, Task, Crew
from typing import List
from crewai import LLM
from pydantic import BaseModel, Field, conlist

files = {
    'agents': './agents/agents.yaml',
    'tasks': './agents/tasks.yaml'
}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

# Assign loaded configurations to specific variables
agents_config = configs['agents']
tasks_config = configs['tasks']

llm = LLM(
    model="ollama/qwen2.5:14b", 
    base_url="http://localhost:11434"
)

llm = LLM(
    model="gpt-4o-mini",
    #base_url="https://api.your-provider.com/v1",
    api_key=""
)

# Creating Agents
query_analysis_agent = Agent(
    config=agents_config['query_analysis_agent'],
    llm=llm
)

web_scraper_agent = Agent(
    config=agents_config['web_scraper_agent'],
    llm=llm
)

campaign_summary_agent = Agent(
    config=agents_config['campaign_summary_agent'],
    llm=llm
)

price_calculation_agent = Agent(
    config=agents_config['price_calculation_agent'],
    llm=llm
)

report_generation_agent = Agent(
    config=agents_config['report_generation_agent'],
    llm=llm
)

# Creating Tasks
task_query_analysis = Task(
    config=tasks_config['query_analysis'],
    agent=query_analysis_agent
)

from crewai.tools import tool
from playwright.sync_api import sync_playwright
import pytesseract
from PIL import Image
import io
import requests
from bs4 import BeautifulSoup

@tool("web_searcher")
def web_searcher(url: str) -> str:
    """
    Extrae el contenido textual de una página web, incluyendo contenido dinámico generado por JavaScript y texto en imágenes.
    
    Argumentos:
    - url (str): La URL de la página web a extraer.
    
    Retorno:
    - str: El contenido textual renderizado de la página web, incluyendo texto extraído de imágenes.
    """
    try:
        with sync_playwright() as p:
            # Lanzar un navegador sin interfaz gráfica
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Cargar la URL y esperar que el contenido se cargue
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")

            # Extraer el texto visible en la página
            text = page.inner_text("body").strip()

            # Extraer todas las imágenes de la página
            image_elements = page.query_selector_all("img")
            ocr_text = []
            
            for img in image_elements:
                img_src = img.get_attribute("src")
                if img_src:
                    try:
                        # Descargar la imagen
                        response = requests.get(img_src, stream=True)
                        response.raise_for_status()
                        img_data = Image.open(io.BytesIO(response.content))

                        # Aplicar OCR para extraer texto de la imagen
                        extracted_text = pytesseract.image_to_string(img_data)
                        ocr_text.append(extracted_text.strip())
                    except Exception as e:
                        ocr_text.append(f"[Error procesando imagen {img_src}: {e}]")

            # Cerrar el navegador
            browser.close()

            # Combinar el texto de la página con el texto extraído de las imágenes
            combined_text = text + "\n\n" + "\n".join(ocr_text)

            return combined_text
    except Exception as e:
        return f"Error al procesar la página web: {e}"


@tool("google_searcher")
def google_searcher(query: str) -> list:
    """
    Realiza una búsqueda en Google y devuelve una lista de resultados, 
    incluyendo enlaces orgánicos y patrocinados (ads).
    
    Parámetros:
    - query (str): La consulta de búsqueda. Se formatea automáticamente para usar "+" en lugar de espacios.

    Retorno:
    - list: Lista de diccionarios con resultados de búsqueda. Cada resultado tiene:
        - 'type': "organic" para resultados normales o "ad" para anuncios patrocinados.
        - 'title': Título del resultado o anuncio.
        - 'link': URL correspondiente al resultado.
    
    Ejemplo:
    >>> google_search("ofertas luz endesa")
    [
        {'type': 'organic', 'title': 'Tarifas de Luz: Encuentra tu oferta de luz | Endesa', 'link': 'https://www.endesa.com/es/luz-y-gas/luz'},
        {'type': 'organic', 'title': 'Ofertas de Luz y Gas. Ahorra en electricidad y ...', 'link': 'https://www.endesa.com/es/ofertas-luz-gas'},
        {'type': 'ad', 'title': 'Black Friday y 200€ - Llévate 200€ al Black Friday', 'link': 'https://www.endesatarifasluzygas.com/multiproducto'},
        ...
    ]
    """
    try:
        # Reemplaza espacios en blanco por "+" para adaptarse al formato de URL de Google
        formatted_query = query.replace(' ', '+')
        url = f"https://www.google.com/search?q={formatted_query}"

        # Encabezados para evitar bloqueos por parte de Google
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Realiza la solicitud HTTP
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa (código 200)

        # Analiza la página web con BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        # Extrae resultados orgánicos
        for g in soup.find_all('div', class_='tF2Cxc'):
            title_tag = g.find('h3')  # Busca el título del resultado
            link_tag = g.find('a', href=True)  # Busca el enlace del resultado
            if title_tag and link_tag:
                results.append({
                    'type': 'organic',  # Etiqueta como resultado orgánico
                    'title': title_tag.text,
                    'link': link_tag['href']
                })

        # Extrae anuncios patrocinados
        for ad in soup.find_all('div', class_='uEierd'):  # Clase específica para contenedores de anuncios
            ad_link_tag = ad.find('a', href=True)  # Busca el enlace del anuncio
            ad_title_tag = ad.find('div', class_='v5yQqb')  # Busca el título del anuncio

            if ad_link_tag and ad_title_tag:
                results.append({
                    'type': 'ad',  # Etiqueta como anuncio patrocinado
                    'title': ad_title_tag.text,
                    'link': ad_link_tag['href']
                })

        return results

    except requests.exceptions.RequestException as e:
        # Maneja errores de conexión y otros problemas de solicitudes
        return [{"error": f"Error al realizar la búsqueda: {e}"}]
    except Exception as e:
        # Maneja cualquier otro error inesperado
        return [{"error": f"Error inesperado: {e}"}]


task_web_scraping = Task(
    config=tasks_config['web_scraping'],
    agent=web_scraper_agent,
    context=[task_query_analysis],
    tools=[google_searcher, web_searcher]
)

task_campaign_summary = Task(
    config=tasks_config['campaign_summary'],
    agent=campaign_summary_agent,
    context=[task_web_scraping]
)

task_price_calculation = Task(
    config=tasks_config['price_calculation'],
    agent=price_calculation_agent,
    context=[task_campaign_summary]
)

task_report_generation = Task(
    config=tasks_config['report_generation'],
    agent=report_generation_agent,
    context=[task_campaign_summary, task_price_calculation]
)

# Creating Crew
crew = Crew(
    agents=[
        query_analysis_agent,
        web_scraper_agent,
        campaign_summary_agent,
        price_calculation_agent,
        report_generation_agent
    ],
    tasks=[
        task_query_analysis,
        task_web_scraping,
        task_campaign_summary,
        task_price_calculation,
        task_report_generation
    ],
    verbose=True
)

## Inputs del proyecto
user_input = "resume la campaña de blackfriday 2024 de octopus, endesa y naturgy. Incluye referencias y links al origen de la información"

inputs = {
    'user_input': user_input
}

# Run the crew
result = crew.kickoff(inputs=inputs)

# Output the result
print(result)

result2=result

with open("informe.md", "w") as file:
    file.write(result.raw)

from markdown_pdf import MarkdownPdf, Section

with open("informe.md", 'r', encoding='utf-8') as file:
    contenido = file.read()

pdf = MarkdownPdf()
pdf.meta["title"] = 'Title'
pdf.add_section(Section(contenido, toc=False))
pdf.save('output.pdf')
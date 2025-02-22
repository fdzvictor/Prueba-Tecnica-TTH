# Multipurpose RAG

## Descripción

Este proyecto implementa un sistema de Recuperación Aumentada Generativa (RAG) para proporcionar información sobre cualquier documento que le incluyas en formato .txt, .docx o .pdf. El modelo usa el LLM de OpenAI (Permite elegir entre GPT-4o o GPT-4o-mini) para dar respuestas. En este caso, proponemos su uso con información de reviews de coches, extraídas de la web KM77.

## Funcionalidades

Ingesta y procesamiento de datos: Captura información desde artículos y fuentes numéricas.

Base de datos vectorial: Indexa datos relevantes para una recuperación eficiente de forma local, usando ChromaDB.

Recuperación de información: Identifica y devuelve información relevante según la consulta del usuario.

Generación de respuestas: Usa un modelo de lenguaje (LLM) para estructurar respuestas informativas.

Interfaz interactiva: Despliegue mediante Streamlit para una experiencia de usuario fluida.

## Tecnologías utilizadas

Base de datos: Base de datos vectorial (ChromaDB).

Procesamiento de datos: Python, usando principalmente las funcionalidades de Langchain.

Modelos de Machine Learning: OpenAI GPT-4o & GPT-4o-mini.

Web scraping: Selenium y BeautifulSoup para obtener información relevante.

Frontend: Streamlit para interacción con el usuario.

## Instalación

Clona el repositorio:

python´´´
git clone https://github.com/tu_usuario/RAG_Coches.git
cd RAG_Coches
```

### Instalación de dependencias

pip install -r requirements.txt

Configura las variables de entorno (API keys,entorno virtual, etc.).

### Ejecuta la aplicación:
python '''
streamlit run app.py  
'''

## Uso
- Una vez incluida tu clave de OPENAI, puedes implementar los datos que se sugieren en la carpeta "Documentos"
1- Introduce una consulta sobre un modelo de coche.

El sistema buscará información en la base de datos vectorial.

Generará una respuesta basada en los datos más relevantes.


Agradecimientos:

Este proyecto se ha realizado gracias a la aportación de @enricdb


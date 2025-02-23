# Multipurpose RAG

## Descripción

Este proyecto implementa un sistema de Recuperación Aumentada Generativa (RAG) para proporcionar información sobre cualquier documento que le incluyas en formato `.txt`, `.docx` o `.pdf`. El modelo usa el LLM de OpenAI (permite elegir entre `GPT-4o` o `GPT-4o-mini`) para dar respuestas. En este caso, proponemos su uso con información de la estadística de hipotecas del INE para 2024.

## Funcionalidades

- **Ingesta y procesamiento de datos**: Captura información desde artículos y fuentes numéricas.
- **Base de datos vectorial**: Indexa datos relevantes para una recuperación eficiente de forma local, usando `ChromaDB`.
- **Recuperación de información**: Identifica y devuelve información relevante según la consulta del usuario.
- **Generación de respuestas**: Usa un modelo de lenguaje (LLM) para estructurar respuestas informativas.
- **Interfaz interactiva**: Despliegue mediante `Streamlit` para una experiencia de usuario fluida.

## Tecnologías utilizadas

- **Base de datos**: Base de datos vectorial (`ChromaDB`).
- **Procesamiento de datos**: `Python`, usando principalmente las funcionalidades de `Langchain`.
- **Modelos de Machine Learning**: `OpenAI GPT-4o` & `GPT-4o-mini`.
- **Web scraping**: `Selenium` y `BeautifulSoup` para obtener información relevante.
- **Frontend**: `Streamlit` para interacción con el usuario.

## Instalación

Clona el repositorio:

```bash
git clone <this-repo-url>
cd <this-repo-folder>
```
### Configura las variables de entorno (Entorno virtual, etc.).

```bash
python -m venv venv

venv\Scripts\activate  # or source venv/bin/activate in Linux/Mac

```

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

### Ejecuta la aplicación

```bash
streamlit run app.py  
```

## Uso

1. Una vez incluida tu clave de `OPENAI`, puedes cargar los documentos que desees, siempre que cumplan con las restriccionesde formato y tamaño.
2. Introduce una consulta sobre tu documento, en este caso presentamos un ejemplo con la nota de prensa sobre hipotecas del INE.
3. El sistema buscará información en la base de datos vectorial.
4. Generará una respuesta basada en los datos más relevantes.

## Agradecimientos

Este proyecto se ha realizado gracias a la aportación de [@enricd](https://github.com/enricd) en GitHub.

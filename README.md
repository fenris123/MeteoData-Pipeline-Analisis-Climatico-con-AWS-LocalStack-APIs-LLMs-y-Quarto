# Meteo-Insight-Pipeline: Ingesta AEMET, Almacenamiento S3 (LocalStack) y Análisis Inteligente con LLM

Este repositorio contiene un pipeline de datos (ETL) automatizado de extremo a extremo que realiza la ingesta de series climatológicas históricas de la API de la AEMET, gestiona su persistencia lógica en un entorno de almacenamiento en la nube simulado (AWS S3) y utiliza Inteligencia Artificial (LLM) para procesar e interpretar los datos brutos, añade graficas conpython transformándolos en informes analíticos visuales en formato HTML y PDF mediante Quarto.



##  Buenas Prácticas de Seguridad y Configuración Local

>  **Nota Importante sobre Seguridad:** Siguiendo las directrices de seguridad en entornos de producción, este repositorio **no expone credenciales, tokens, direcciones IP privadas ni puertos locales** en el código público. 

Toda la infraestructura y los secretos se gestionan mediante variables de entorno. Para ejecutar este proyecto de forma local en tu máquina, es necesario configurar un archivo de credenciales externo.  (.env)

### Configuración del Archivo `.env` (o `.env` equivalente)
El script de ingesta busca por defecto las credenciales en un entorno gestionado de forma centralizada en la ruta de red configurada en el código. Si clonas este repositorio, asegúrate de crear un archivo con la extensión correspondiente (`tokens.env` o `.env`) que contenga las siguientes variables obligatorias:

LOCALSTACK_ENDPOINT=http://<IP_DE_TU_NAS_O_LOCALHOST>:<PUERTO_DE_DOCKER>
AWS_ACCESS_KEY_ID=mock_key
AWS_SECRET_ACCESS_KEY=mock_secret
TOKEN_AEMET=token_real_de_la_API_aemet

Ademas  en el archivo p1_aemet_actualizador.py y p2_aemet_extractor.py deberas ajustar la ruta del archivo .env, en la linea siguiente:
load_dotenv("Y:/espaciopython/enviroments/tokens.env")


## 🏗️ Arquitectura y Flujo de Datos

El pipeline opera de forma completamente desacoplada siguiendo el siguiente flujo de procesamiento:

1. **Ingesta (API -> S3):** Se mira si los datos del mes a estudiar ya estan en nuestro S3 (periodo = ultimos 50 años), y si no se descargan los que falten usando la API de aemet .
2. **Extraccion (S3 -> DataFrame):** Los datos se estructuran, limpian y consolidan en memoria.
3. **Visualización:** Se computan estadísticas descriptivas (medias y desviaciones estándar ±2 std) y se generan graficas. 
4. **Análisis por IA (LLM):** Se formatea un prompt con los datos agregados históricos frente al año actual y se envía a un modelo local para sacar el analisis via texto.
5. **Compilación (Quarto):** Se orquesta la generación de un reporte dinámico final.


## Infraestructura empleada

El proyecto destaca por resolver retos reales de infraestructura mediante un entorno local distribuido:
* **Servidor NAS (ZimaOS, linux):** Aloja nuestro docker.
* **AWS S3 (LocalStack v1.4.0):** Desplegado mediante un contenedor Docker estándar en la NAS para simular el almacenamiento cloud de AWS de manera gratuita y sin fricciones de licencias u OAuth.
* **Ordenador local (Windows):** Ejecuta el orquestador principal de Python, consume el LLM local y renderiza el informe final.

---

## Requisitos y Librerías Necesarias

Para ejecutar este pipeline se ha empleado Python 3.13.1, Quarto, Ollama con el modelo Llama 3.1:8b en el sistema local, junto con un contenedor Docker de LocalStack v1.4.0 desplegado de forma nativa en una NAS con ZimaOS.

Instala las librerias de Python ejecutando:

pip install boto3 pandas requests python-dotenv matplotlib


## Aviso de Propiedad Intelectual y Regulaciones de Uso 
Los datos climatológicos empleados en este proyecto se obtienen de la API OpenData de la Agencia Estatal de Meteorología (AEMET). El uso, redistribución o explotación de esta información queda sujeto de forma estricta a las condiciones y notas legales específicas de la AEMET, las cuales deben ser consultadas en su portal oficial.

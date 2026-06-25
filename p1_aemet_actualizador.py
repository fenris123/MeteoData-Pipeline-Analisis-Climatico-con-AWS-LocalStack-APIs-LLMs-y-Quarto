# pip install boto3 requests python-dotenv

import os
import json
import calendar
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

import boto3

# =========================
# PASO 0: CARGA DE ENTORNO Y VARIABLES
# =========================

load_dotenv("Y:/espaciopython/enviroments/tokens.env")

LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

BUCKET = "aemet-data"
ESTACION_DEFAULT = "5783"

# CORREGIDO: Usamos TOKEN_AEMET tal cual está en tu entorno funcional
TOKEN = os.getenv("TOKEN_AEMET")
headers = {
    "accept": "application/json",
    "api_key": TOKEN
}

URL_BASE = "https://opendata.aemet.es/opendata"


# =========================
# PASO 1: CLIENTE S3 (LOCALSTACK)
# =========================

s3 = boto3.client(
    "s3",
    endpoint_url=LOCALSTACK_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name="us-east-1"
)

# =========================
# PASO 2: FUNCIONES S3 (HELPERS)
# =========================

def generar_key_s3(station, year, month):
    return f"aemet/{station}/{year}/{month:02d}.json"


def existe_en_s3(key):
    try:
        s3.head_object(Bucket=BUCKET, Key=key)
        return True
    except:
        return False


def subir_a_s3(key, data):
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json"
    )

def crear_bucket_si_no_existe():
    try:
        s3.head_bucket(Bucket=BUCKET)
        print(f"✔ Bucket existe: {BUCKET}")
    except:
        print(f"📦 Creando bucket: {BUCKET}")
        s3.create_bucket(Bucket=BUCKET)


# =========================
# PASO 3: CONSUMO API AEMET (CORREGIDO Y VALIDADO)
# =========================

def descargar_aemet(year, month, station):
    ultimo_dia = calendar.monthrange(year, month)[1]

    fecha_ini = f"{year}-{month:02d}-01T00:00:00UTC"
    fecha_fin = f"{year}-{month:02d}-{ultimo_dia:02d}T23:59:59UTC"

    endpoint = (
        f"/api/valores/climatologicos/diarios/datos/"
        f"fechaini/{fecha_ini}/"
        f"fechafin/{fecha_fin}/"
        f"estacion/{station}"
    )

    try:
        r = requests.get(URL_BASE + endpoint, headers=headers, timeout=10)


        # --- CONTROL ANTIBANEO (HTTP 429) ---
        if r.status_code == 429:
            print("🛑 ¡Oops! HTTP 429 (Límite superado). Durmiendo 60 segundos para enfriar la API...")
            time.sleep(90)
            r = requests.get(URL_BASE + endpoint, headers=headers, timeout=10)

            # Si el reintento post-siesta sigue fallando (ej. 429 o 500), salimos ya
            if r.status_code != 200:
                print(f"⚠️ HTTP {r.status_code} en {year}-{month:02d}")
                return None


        if r.status_code != 200:
            print(f"⚠️ HTTP {r.status_code} en {year}-{month:02d}")
            return None

        meta = r.json()
    except Exception as e:
        print(f"⚠️ Error en petición de metadatos ({year}-{month:02d}): {e}")
        return None

    # OJO: La AEMET a veces devuelve un 200 pero con un estado de error interno
    if meta.get("estado") and meta.get("estado") != 200:
        print(f"⚠️ AEMET API Error {meta.get('estado')}: {meta.get('descripcion')} ({year}-{month:02d})")
        return None

    datos_url = meta.get("datos")
    if not datos_url:
        print(f"⚠️ Sin URL de datos ({year}-{month:02d})")
        return None

    # Segunda petición: descarga del archivo JSON final
    try:
        r2 = requests.get(datos_url, timeout=10)
        r2.raise_for_status()
        data_final = json.loads(r2.text)

        # Validar que realmente contenga una lista con registros válidos
        if isinstance(data_final, list) and len(data_final) > 0:
            return data_final
        else:
            print(f"⚠️ JSON vacío o formato incorrecto en {year}-{month:02d}")
            return None

    except Exception as e:
        print(f"⚠️ Error al obtener o parsear los datos finales ({year}-{month:02d}): {e}")
        return None

# =========================
# PASO 4: LÓGICA PRINCIPAL DEL PIPELINE
# =========================

def ejecutar(month, station=ESTACION_DEFAULT):
    crear_bucket_si_no_existe()

    año_actual = datetime.now().year
    rango_años = range(año_actual - 50, año_actual + 1)

    for year in rango_años:
        key = generar_key_s3(station, year, month)
        forzar_actualizacion = (year == año_actual)

        if not forzar_actualizacion and existe_en_s3(key):
            print(f"✔ Ya existe en S3: {key}")
            continue

        print(f"📥 Descargando {year}-{month:02d}...")
        datos = descargar_aemet(year, month, station)

        # CRUCIAL: Solo subimos a S3 si los datos son válidos y contienen información
        if datos:
            subir_a_s3(key, datos)
            print(f"⬆ Guardado con éxito: {key}")
        else:
            print(f"❌ Saltado {year}-{month:02d} debido a error o falta de datos.")

        # Respetar la API para evitar baneos de IP (AEMET es muy estricta)
        time.sleep(5)


# =========================
# PASO 5: EJECUCIÓN
# =========================

if __name__ == "__main__":
    mes = int(input("Mes (1-12): "))
    estacion = input(f"Estación. (Enter = {ESTACION_DEFAULT}): ") or ESTACION_DEFAULT

    ejecutar(mes, estacion)
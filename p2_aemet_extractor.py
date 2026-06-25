# pip install boto3 pandas python-dotenv

import os
import json
import boto3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# =========================
# PASO 0: CARGA DE ENTORNO Y VARIABLES
# =========================
load_dotenv("Y:/espaciopython/enviroments/tokens.env")

LOCALSTACK_ENDPOINT = os.getenv("LOCALSTACK_ENDPOINT")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

BUCKET = "aemet-data"


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
# PASO 2: LÓGICA DE EXTRACCIÓN (S3 A DATAFRAME)
# =========================
def extraer_datos_a_dataframe(mes, estacion):
    año_actual = datetime.now().year
    rango_años = range(año_actual - 50, año_actual + 1)

    registros_totales = []

    print(f"🔍 Extrayendo datos de S3 para la estación {estacion} (Mes: {mes:02d})...")

    for year in rango_años:
        key = f"aemet/{estacion}/{year}/{mes:02d}.json"

        try:
            response = s3.get_object(Bucket=BUCKET, Key=key)
            json_data = response["Body"].read().decode("utf-8")
            mes_datos = json.loads(json_data)

            if isinstance(mes_datos, list):
                registros_totales.extend(mes_datos)

        except s3.exceptions.NoSuchKey:
            continue
        except Exception as e:
            print(f"⚠️ Error inesperado al leer {key}: {e}")
            continue

    if not registros_totales:
        print("❌ No se encontraron datos en S3 para los parámetros indicados.")
        return pd.DataFrame()

    # =========================
    # PASO 3: LIMPIEZA, ESTRUCTURA Y EXPORTACIÓN OPCIONAL
    # =========================
    df = pd.DataFrame(registros_totales)

    df = df[["fecha", "tmax", "tmin"]]
    df["fecha"] = pd.to_datetime(df["fecha"])

    df["tmax"] = pd.to_numeric(df["tmax"].astype(str).str.replace(",", "."), errors="coerce")
    df["tmin"] = pd.to_numeric(df["tmin"].astype(str).str.replace(",", "."), errors="coerce")

    df = df.dropna(subset=["tmax", "tmin"])

    df["dia"] = df["fecha"].dt.day
    df["anio"] = df["fecha"].dt.year

    print(f"✅ Extracción completada. Se han cargado {len(df)} registros diarios.")

    # Pregunta interactiva obligatoria (Sale siempre)
    guardar = input("\n💾 ¿Quieres guardar estos datos en un archivo CSV para uso posterior? (si/no): ").strip().lower()

    if guardar in ["si", "s", "yes", "y"]:
        # 1. Obtenemos el directorio exacto donde reside este script de Python
        directorio_script = os.path.dirname(os.path.abspath(__file__))

        # 2. Construimos la ruta absoluta hacia la carpeta "datos" dentro de ese directorio
        carpeta_salida = os.path.join(directorio_script, "datos")

        # 3. Creamos la carpeta si no existe
        if not os.path.exists(carpeta_salida):
            os.makedirs(carpeta_salida)
            print(f"📦 Creando carpeta local: {carpeta_salida}")

        # 4. Creamos el archivo CSV con su ruta absoluta final
        nombre_archivo = os.path.join(carpeta_salida, f"aemet_{estacion}_{mes:02d}.csv")
        df.to_csv(nombre_archivo, index=False)
        print(f"💾 ¡Archivo guardado con éxito en: {nombre_archivo}!\n")

    return df



# =========================
# PASO 4: PRUEBA LOCAL (AISLADA)
# =========================
if __name__ == "__main__":
    mes_test = int(input("Introduce mes a extraer (1-12): "))
    estacion_test = input("Introduce idema (ENTER = 5783): ") or "5783"

    df_prueba = extraer_datos_a_dataframe(mes=mes_test, estacion=estacion_test)
    if not df_prueba.empty:
        print("\n--- Primeras filas del DataFrame en memoria ---")
        print(df_prueba.head())


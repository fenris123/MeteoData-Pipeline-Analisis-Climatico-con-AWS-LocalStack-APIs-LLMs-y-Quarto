# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 13:25:30 2026

@author: fenris123
"""

# pip install requests pandas

import os
from datetime import datetime
import requests


# =========================
# PASO 0: CONFIGURACIÓN DE RUTA ABSOLUTA DE SALIDA
# =========================
directorio_script = os.path.dirname(os.path.abspath(__file__))
# Creamos la ruta hacia la carpeta "resumen"
carpeta_resumen = os.path.join(directorio_script, "resumen")

if not os.path.exists(carpeta_resumen):
    os.makedirs(carpeta_resumen)

RUTA_RESUMEN_MD = os.path.join(carpeta_resumen, "resumen_llm.md")


# =========================
# PASO 1: FUNCIÓN DE CONEXIÓN CON OLLAMA
# =========================
def ask_llama(prompt):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
        }
    )
    return r.json()["response"]


# =========================
# PASO 2: FUNCIÓN PRINCIPAL DE ANÁLISIS (EL BLOQUE PIPELINE)
# =========================
def analizar_clima_con_llm(df, mes):
    año_actual = datetime.now().year

    # Separamos los datos usando las columnas de apoyo que creó el extractor
    df_hist = df[df["anio"] < año_actual]
    df_act = df[df["anio"] == año_actual]

    # Agrupaciones para el Histórico (Media, Min, Max por día)
    hist = df_hist.groupby("dia").agg({
        "tmax": ["mean", "min", "max"],
        "tmin": ["mean", "min", "max"]
    })
    hist.columns = ["_".join(c) for c in hist.columns]
    hist = hist.reset_index()

    # Agrupaciones para el Año Actual
    act = df_act.groupby("dia").agg({
        "tmax": ["mean", "min", "max"],
        "tmin": ["mean", "min", "max"]
    })
    act.columns = ["_".join(c) for c in act.columns]
    act = act.reset_index()

    # =========================
    # PASO 3: LLM PROMPT
    # =========================
    prompt = f"""
Eres un analista meteorológico.

Compara clima histórico (50 años) vs año actual para el mes {mes:02d}.

HISTÓRICO (por día del mes):
{hist.to_string(index=False)}

AÑO ACTUAL:
{act.to_string(index=False)}

Genera:
1. Resumen general del comportamiento del mes
2. Anomalías térmicas relevantes
3. Días más extremos
4. Conclusión clara en lenguaje natural
"""

    print("\n🤖 Consultando LLM (Llama 3.1:8b)...")
    resumen = ask_llama(prompt)

    # =========================
    # PASO 4: GUARDAR OUTPUT DE FORMA ABSOLUTA
    # =========================
    # Al guardarlo aquí de forma absoluta, Quarto podrá leerlo sin perderse
    with open(RUTA_RESUMEN_MD, "w", encoding="utf-8") as f:
        f.write(resumen)

    print(f"📝 Archivo de texto guardado con éxito en: {RUTA_RESUMEN_MD}\n")
    return resumen


# =========================
# PASO 5: PRUEBA LOCAL (AISLADA)
# =========================
if __name__ == "__main__":
    try:
        from p2_aemet_extractor import extraer_datos_a_dataframe

        print("🧪 Probando el módulo del LLM de forma aislada...")
        mes_test = 6
        df_test = extraer_datos_a_dataframe(mes=mes_test, estacion="5783")

        if not df_test.empty:
            analizar_clima_con_llm(df_test, mes=mes_test)

    except ImportError:
        print("⚠️ Recuerda que para probar este script suelto necesitas tener 'p2_aemet_extractor.py' en la misma carpeta.")
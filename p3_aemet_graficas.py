# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 13:14:13 2026

@author: fenris123
"""

# pip install matplotlib pandas

import os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# =========================
# PASO 0: CONFIGURACIÓN DE RUTAS ABSOLUTAS
# =========================
# Definimos de forma segura dónde se guardarán las imágenes (Carpeta "graficos" al lado del script)
directorio_script = os.path.dirname(os.path.abspath(__file__))
CARPETA_GRAFICOS = os.path.join(directorio_script, "graficos")

if not os.path.exists(CARPETA_GRAFICOS):
    os.makedirs(CARPETA_GRAFICOS)


# =========================
# PASO 1: FUNCIÓN PRINCIPAL DE GENERACIÓN
# =========================
def generar_graficos_clima(df, mes):
    """
    Toma el DataFrame consolidado y genera los 3 gráficos clave:
    Scatter general, Bandas Tmax y Bandas Tmin.
    Guarda los archivos en /graficos y los muestra en Spyder.
    """
    año_actual = datetime.now().year

    # Separación de históricos vs año actual
    df_hist = df[df["anio"] < año_actual]
    df_act = df[df["anio"] == año_actual]

    # =========================
    # PASO 2: GRÁFICO 1 (SCATTER MULTIVARIABLE)
    # =========================
    plt.figure(figsize=(12, 6))

    plt.scatter(df_hist["dia"], df_hist["tmax"], facecolors="none", edgecolors="red", alpha=0.6, label="Tmax hist")
    plt.scatter(df_hist["dia"], df_hist["tmin"], facecolors="none", edgecolors="blue", alpha=0.6, label="Tmin hist")

    plt.scatter(df_act["dia"], df_act["tmax"], color="black", marker="^", s=60, label="Tmax actual")
    plt.scatter(df_act["dia"], df_act["tmin"], color="black", marker="v", s=60, label="Tmin actual")

    plt.legend()
    plt.title(f"Dispersión de Temperaturas - Mes {mes:02d}")
    plt.xlabel("Día del Mes")
    plt.ylabel("Temperatura (ºC)")
    plt.grid(True, linestyle="--", alpha=0.5)

    # Guardado absoluto para Quarto
    ruta_scatter = os.path.join(CARPETA_GRAFICOS, "scatter.png")
    plt.savefig(ruta_scatter, dpi=150, bbox_inches="tight")
    plt.show() # <-- Obliga a Spyder a pintarlo en su panel de Plots


    # =========================
    # PASO 3: CÁLCULO DE ESTADÍSTICAS (BANDAS)
    # =========================
    stats_max = df_hist.groupby("dia")["tmax"].agg(mean="mean", std="std").reset_index()
    stats_max["upper"] = stats_max["mean"] + (2 * stats_max["std"])
    stats_max["lower"] = stats_max["mean"] - (2 * stats_max["std"])

    stats_min = df_hist.groupby("dia")["tmin"].agg(mean="mean", std="std").reset_index()
    stats_min["upper"] = stats_min["mean"] + (2 * stats_min["std"])
    stats_min["lower"] = stats_min["mean"] - (2 * stats_min["std"])


    # =========================
    # PASO 4: GRÁFICO 2 (BANDAS TMAX)
    # =========================
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(stats_max['dia'], stats_max['mean'], label='Media Tmax Histórica', color='black', linewidth=2)
    ax.plot(stats_max['dia'], stats_max['upper'], color='red', linestyle='--', linewidth=1.5)
    ax.plot(stats_max['dia'], stats_max['lower'], color='red', linestyle='--', linewidth=1.5)

    ax.fill_between(stats_max['dia'], stats_max['lower'], stats_max['upper'], color='red', alpha=0.15, label='Desviación Estándar (±1 std)')

    ax.scatter(df_act["dia"], df_act["tmax"], color="red", edgecolors="black", marker="^", s=80, label="Tmax actual")

    ax.legend()
    ax.set_title(f"Análisis de Bandas - Temperatura Máxima (Mes {mes:02d})")
    ax.set_xlabel("Día del Mes")
    ax.set_ylabel("Temperatura (ºC)")
    ax.grid(True, linestyle="--", alpha=0.5)

    ruta_tmax = os.path.join(CARPETA_GRAFICOS, "tmax_bandas.png")
    plt.savefig(ruta_tmax, dpi=150, bbox_inches="tight")
    plt.show()


    # =========================
    # PASO 5: GRÁFICO 3 (BANDAS TMIN)
    # =========================
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(stats_min['dia'], stats_min['mean'], label='Media Tmin Histórica', color='black', linewidth=2)
    ax.plot(stats_min['dia'], stats_min['upper'], color='#1f77b4', linestyle='--', linewidth=1.5)
    ax.plot(stats_min['dia'], stats_min['lower'], color='#1f77b4', linestyle='--', linewidth=1.5)

    ax.fill_between(stats_min['dia'], stats_min['lower'], stats_min['upper'], color='#1f77b4', alpha=0.15, label='Desviación Estándar (±1 std)')

    ax.scatter(df_act["dia"], df_act["tmin"], color="blue", edgecolors="black", marker="v", s=80, label="Tmin actual")

    ax.legend()
    ax.set_title(f"Análisis de Bandas - Temperatura Mínima (Mes {mes:02d})")
    ax.set_xlabel("Día del Mes")
    ax.set_ylabel("Temperatura (ºC)")
    ax.grid(True, linestyle="--", alpha=0.5)

    ruta_tmin = os.path.join(CARPETA_GRAFICOS, "tmin_bandas.png")
    plt.savefig(ruta_tmin, dpi=150, bbox_inches="tight")
    plt.show()

    print(f"📊 Gráficos guardados con éxito en la carpeta: {CARPETA_GRAFICOS}")


# =========================
# PASO 6: PRUEBA LOCAL (AISLADA)
# =========================
if __name__ == "__main__":
    # Importamos tu extractor para hacer un test rápido si ejecutas este archivo suelto
    # Nota: Asegúrate de que 2_aemet_extractor.py esté en la misma carpeta
    try:
        from p2_aemet_extractor import extraer_datos_a_dataframe

        print("🧪 Lanzando prueba aislada de gráficos...")
        mes_test = 6
        df_test = extraer_datos_a_dataframe(mes=mes_test, estacion="5783")

        if not df_test.empty:
            generar_graficos_clima(df_test, mes=mes_test)
    except ImportError:
        print("⚠️ Para probar este script de forma aislada, necesitas tener '2_aemet_extractor.py' en el mismo directorio.")
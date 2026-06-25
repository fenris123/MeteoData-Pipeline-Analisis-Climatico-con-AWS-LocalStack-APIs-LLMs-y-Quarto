# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 19:58:46 2026

@author: fenris123
"""
# pip install python-dotenv

import os
import subprocess
import shutil
import tempfile
from datetime import datetime

# =========================
# PASO 0: CONFIGURACIÓN DE RUTAS RELATIVAS AL WORKING DIRECTORY (WD)
# =========================

# Capturamos de forma dinámica el Directorio de Trabajo actual donde está este script
directorio_wd = os.path.dirname(os.path.abspath(__file__))

# Rutas de entrada reales dentro de tu WD (donde p3 y p4 guardaron las cosas)
RUTA_RESUMEN_WD = os.path.join(directorio_wd, "resumen", "resumen_llm.md")
CARPETA_GRAFICOS_WD = os.path.join(directorio_wd, "graficos")

# Carpeta de salida definitiva dentro de tu WD
CARPETA_REPORTE_FINAL = os.path.join(directorio_wd, "reporte")
if not os.path.exists(CARPETA_REPORTE_FINAL):
    os.makedirs(CARPETA_REPORTE_FINAL)


# =========================
# PASO 1: FUNCIÓN PRINCIPAL CON ENTORNO TEMPORAL LOCAL
# =========================


  #####  IMPORTANTE #####
  #####  IMPORTANTE #####
  #####  IMPORTANTE #####

  # Estamos dando un paso de guardado temporal en C: con posterior copiado y pegado  al WD.
  # Esto se debe a que mi WD esta en una NAS y Quarto no lo admite  bien trabajando ahi directamente
  # Si se trabaja directamente con el script en el disco local, esto no es necesario.

  #####  IMPORTANTE #####
  #####  IMPORTANTE #####
  #####  IMPORTANTE #####




def generar_reporte_quarto(mes, estacion):
    año_actual = datetime.now().year

    # 1. Leemos el resumen del LLM desde tu WD antes de irnos al temporal
    if os.path.exists(RUTA_RESUMEN_WD):
        with open(RUTA_RESUMEN_WD, "r", encoding="utf-8") as f:
            resumen_analista = f.read()
    else:
        resumen_analista = "*Análisis del LLM no disponible.*"

    # 2. Creamos una carpeta temporal segura en el disco local C: de tu máquina
    with tempfile.TemporaryDirectory(prefix="quarto_local_") as dir_temporal_local:
        print(f"📁 Entorno de compilación local creado en C:: {dir_temporal_local}")

        # Copiamos los gráficos desde tu WD al disco local C: para que Quarto los tenga al lado
        for archivo in ["scatter.png", "tmax_bandas.png", "tmin_bandas.png"]:
            origen = os.path.join(CARPETA_GRAFICOS_WD, archivo)
            if os.path.exists(origen):
                shutil.copy(origen, dir_temporal_local)


        # =========================
        # PASO 2: CONTENIDO DE LA PLANTILLA (.QMD) EN LOCAL
        # =========================

        reporte_content = f"""---
title: "Análisis Meteorológico Histórico vs Actual - Estación {estacion} (Mes: {mes:02d} / Año: {año_actual})"
author: "Guillermo Ferrer. Algunos Textos generados por Llama"
date: "{datetime.now().strftime('%Y-%m-%d')}"
format:
  html: {{}}
  pdf:
    fig-pos: 'H'
    header-includes:
      - \\usepackage{{float}}
---

## Resumen del Analista (LLM)

{resumen_analista}

---

\\pagebreak
## Visualización de Datos Seleccionados

### Comparativa de Dispersión General
En este gráfico se muestran todos los puntos históricos de los últimos 50 años (círculos) frente a los valores registrados en el año actual (triángulos).

![Dispersión de Temperaturas del Mes](scatter.png)

\\pagebreak
### Análisis de Bandas - Temperatura Máxima
Media histórica acumulada frente a los valores máximos de este año, incluyendo las bandas de la desviación estándar (±2 std).

![Bandas Temperatura Máxima](tmax_bandas.png)

\\pagebreak
### Análisis de Bandas - Temperatura Mínima
Media histórica acumulada frente a los valores mínimos de este año, incluyendo las bandas de la desviación estándar (±2 std).

![Bandas Temperatura Mínima](tmin_bandas.png)
"""

        # Escribimos el .qmd temporalmente en el disco local C:
        ruta_qmd_local = os.path.join(dir_temporal_local, "reporte.qmd")
        with open(ruta_qmd_local, "w", encoding="utf-8") as f:
            f.write(reporte_content)



        # =========================
        # PASO 3: COMPILACIÓN LOCAL Y TRASLADO AL WD
        # =========================


        print("🚀 Lanzando Quarto Render localmente en C:...")

        resultado = subprocess.run(
            ["quarto", "render", "reporte.qmd"],
            capture_output=True,
            text=True,
            shell=True,
            cwd=dir_temporal_local  # Forzamos a Quarto a trabajar en C:\... para evitar rollos de red
        )

        if resultado.returncode == 0:
            print("✅ ¡Informe Quarto compilado en local con éxito!")
            print("📦 Guardando reportes finales en la carpeta /reporte de tu WD...")

            # Buscamos los archivos generados en C: y los copiamos a la carpeta 'reporte' de tu WD
            for archivo_salida in ["reporte.qmd", "reporte.html", "reporte.pdf"]:
                ruta_origen = os.path.join(dir_temporal_local, archivo_salida)
                if os.path.exists(ruta_origen):
                    shutil.copy(ruta_origen, CARPETA_REPORTE_FINAL)
                    print(f" └─ Guardado en WD: {os.path.join(CARPETA_REPORTE_FINAL, archivo_salida)}")

            print(f"🎉 Proceso terminado. Archivos disponibles en tu WD: {CARPETA_REPORTE_FINAL}")
        else:
            print("❌ Error en la compilación de Quarto en local C:")
            print(resultado.stderr)

    # Al salir del bloque 'with', Python limpia el disco C: automáticamente
    print("🧹 Entorno temporal local de C: eliminado y limpio.")


# =========================
# PASO 4: PRUEBA LOCAL (AISLADA)
# =========================
if __name__ == "__main__":
    generar_reporte_quarto(mes=6, estacion="5783")
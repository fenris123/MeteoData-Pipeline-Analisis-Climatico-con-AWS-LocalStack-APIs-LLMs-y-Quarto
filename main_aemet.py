# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 20:32:00 2026

@author: fenris123
Título: Orquestador Maestro Completo (Actualización + Pipeline)
"""

import time
import subprocess







# =========================
# PASO 0: INICIO DEL CRONÓMETRO, ENCENDER DOCKER E IMPORTACIONES
# =========================
inicio_proceso = time.time()




# Importamos las funciones principales de tus 5 scripts modulares
try:
    # Adaptado a la función 'ejecutar' original de tu p1
    from p1_aemet_actualizador import ejecutar as actualizar_s3
    from p2_aemet_extractor import extraer_datos_a_dataframe
    from p3_aemet_graficas import generar_graficos_clima
    from p4_aemet_llm import analizar_clima_con_llm
    from p5_aemet_quarto import generar_reporte_quarto
except ImportError as e:
    print("❌ Error crítico: No se encuentran los scripts modulares en este directorio.")
    print(f"Detalle del error: {e}")
    print("Asegúrate de que main_aemet.py esté en la misma carpeta que los scripts p1 a p5.")
    exit()





# =========================
# PASO 1: ENTRADA DE DATOS (INPUTS INTERACTIVOS)
# =========================
ESTACION_POR_DEFECTO = "5783"  # Rota

print("=" * 60)
print("     PIPELINE METEOROLÓGICO AUTOMATIZADO (AEMET + LLM)     ")
print("=" * 60)

try:
    mes_usuario = int(input("📅 Introduce el número del mes a analizar (1-12): "))
    if not (1 <= mes_usuario <= 12):
        print("❌ Error: El mes debe estar entre 1 y 12.")
        exit()
except ValueError:
    print("❌ Error: Debes introducir un número entero.")
    exit()

estacion_usuario = input(f"🏢 Introduce el IDEMA de la estación (ENTER = {ESTACION_POR_DEFECTO}): ").strip()
if not estacion_usuario:
    estacion_usuario = ESTACION_POR_DEFECTO


# =========================
# PASO 2: EJECUCIÓN DE LA CADENA EN MEMORIA (RAM)
# =========================
print("\n🚀 Iniciando el flujo automatizado...\n")

# --- PASO 1: Verificación y descarga (API AEMET -> S3 LocalStack) ---
print("[1/5] Ejecutando p1: Comprobando disponibilidad y actualizando S3...")
# Llamamos a tu función original del p1 pasándole los datos limpitos
actualizar_s3(month=mes_usuario, station=estacion_usuario)

# --- PASO 2: Extracción (De S3 a DataFrame) ---
print("\n" + "-"*40)
print("[2/5] Ejecutando p2: Extrayendo datos de LocalStack S3 a RAM...")
df_clima = extraer_datos_a_dataframe(mes=mes_usuario, estacion=estacion_usuario)

if df_clima is None or df_clima.empty:
    print("❌ Cadena abortada: No se pudieron recuperar datos tras la verificación.")
    exit()

# --- PASO 3: Gráficos (Guarda imágenes en /graficos) ---
print("\n" + "-"*40)
print("[3/5] Ejecutando p3: Generando scatter y análisis de bandas...")
generar_graficos_clima(df_clima, mes=mes_usuario)

# --- PASO 4: IA (Habla con Ollama y guarda en /resumen) ---
print("\n" + "-"*40)
print("[4/5] Ejecutando p4: Enviando datos agregados a Ollama (Llama 3.1)...")
analizar_clima_con_llm(df_clima, mes=mes_usuario)

# --- PASO 5: Quarto (Compila en C: y traslada los reportes finales a /reporte) ---
print("\n" + "-"*40)
print("[5/5] Ejecutando p5: Creando entorno temporal y compilando reporte final...")
generar_reporte_quarto(mes=mes_usuario, estacion=estacion_usuario)






# =========================
# PASO 3: CÓMPUTO DE TIEMPOS Y CIERRE
# =========================





fin_proceso = time.time()
tiempo_total = fin_proceso - inicio_proceso

minutos = int(tiempo_total // 60)
segundos = int(tiempo_total % 60)

print("\n" + "=" * 60)
print("🏁 ¡PIPELINE COMPLETO EJECUTADO CON ÉXITO TOTAL!")
print(f"⏱️ Tiempo total de procesado: {minutos} min {segundos} seg")
print(f"📂 Reportes listos en la carpeta '/reporte' de tu WD.")
print("=" * 60)
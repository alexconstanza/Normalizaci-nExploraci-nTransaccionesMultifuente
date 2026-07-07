# Sistema de Normalización y Exploración de Transacciones Multifuente

Este proyecto implementa una solución robusta y arquitectónica en Python para resolver el problema de la ingesta de datos financieros heterogéneos provenientes de múltiples plataformas origen (Fuentes A, B y C). El sistema automatiza las etapas de detección, limpieza, transformación y cuarentena de transacciones operando bajo un esquema canónico estricto, exponiendo los resultados a través de una interfaz de línea de comandos (CLI) altamente interactiva.

## 📋 Características Principales

- **Detección Dinámica de Fuente:** Identificación en tiempo real del origen de los datos de acuerdo con las firmas estructurales del payload.
- **Motor de Normalización Determinista:**
  - **Fuente A:** Conversión estándar de datos e ISO-estructuras.
  - **Fuente B:** Tratamiento financiero preciso (conversión de enteros/centavos a flotantes mediante división exacta `/ 100.0`).
  - **Fuente C:** Limpieza de cadenas de texto complejas, eliminación de caracteres especiales (símbolos monetarios como `€`), conversión de formato decimal europeo (comas `,` a puntos `.`) e inferencia determinista de divisa.
- **Consolidación Semántica:** Unificación de estados mutables (`completed`, `OK`, `success`) hacia estados canónicos homogéneos (`COMPLETED`, `PENDING`, `FAILED`).
- **Política de Cuarentena Avanzada:** Aislamiento y tipificación transparente de registros corruptos o incompletos con motivos detallados de rechazo para auditoría sin romper el flujo de ejecución.
- **Interfaz Interactiva (CLI):** Visualización modular de métricas financieras, filtrado dinámico en tiempo real y exploración del inventario en cuarentena.

---

## 🏗️ Estructura del Proyecto

El proyecto mantiene una estricta separación de responsabilidades dividida en los siguientes artefactos:

```text
├── app.py                         # Código fuente modular e interactivo (Lógica + CLI)
├── transactions.json              # Dataset de prueba con datos heterogéneos y corruptos
└── nota_tecnica_normalizacion.pdf # Documento formal de decisiones de diseño y arquitectura

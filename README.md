# Normalización y Exploración de Transacciones Multifuente

## 🎯 Objetivo
Normalizar datos heterogéneos, modelarlos correctamente y exponerlos mediante una interfaz interactiva desarrollada en Python, demostrando dominio técnico, criterio de diseño y uso consciente de la IA como apoyo al desarrollo.

## 📝 Descripción de la actividad
Desarrollar un sistema de normalización de transacciones provenientes de múltiples fuentes y permitir su exploración a través de una interfaz interactiva. La actividad se centra en:
* Definir un modelo de datos normalizado.
* Implementar reglas claras de transformación y validación.
* Exponer los datos y métricas de forma usable para un usuario humano.
* La interfaz no debe ser únicamente salida por consola (prints), sino que debe permitir algún grado de interacción (menús, filtros, vistas, etc.)

### Formato de entrada (ejemplo base)
Los registros de transacciones pueden provenir de distintas fuentes y estructuras. El estudiante deberá definir el esquema normalizado final.

---

## ⚙️ Requerimientos funcionales mínimos

### 1. Normalización de datos
El sistema debe:
* Leer transacciones desde un archivo JSON.
* Detectar el tipo o fuente de cada transacción.
* Normalizar todas las transacciones a un formato común.

**Aplicar reglas explícitas:**
* Conversión de montos.
* Normalización de moneda.
* Mapeo de estados.
* Manejo de formatos de fecha.

### 2. Validación y métricas
El sistema debe:
* Identificar transacciones inválidas o incompletas y definir qué hacer con ellas (descartar, marcar, separar).
* Generar métricas: Total procesadas, válidas vs inválidas, conteo por estado y totales por moneda.

### 3. Interfaz interactiva (obligatoria)
El sistema debe incluir una interfaz que permita interactuar con los datos normalizados.

---

## 🏗️ Solución completa diseñada con un enfoque profesional y arquitectónico
Estructura del sistema divido estrictamente cada responsabilidad (Normalización, Validación, Métricas e Interfaz) para asegurar escalabilidad y mantenimiento, aplicando políticas estrictas de control donde la lógica de negocio y esquemas permanecen del lado del desarrollador humano.

El proyecto consta de los siguientes archivos listos para su uso:
* **app.py:** Código fuente modular, interactivo y ejecutable con la arquitectura solicitada.
* **transactions.json:** Datos de prueba para evaluar la robustez del sistema.
* **nota_tecnica_normalizacion.pdf:** Documento de arquitectura de datos y decisiones de diseño formal de una página.

---

## 📑 Resumen del Diseño Estructural Implementado

### 1. Esquema Canónico Final de Datos (Decisión de Diseño Humana)
Para unificar las fuentes presentadas en la imagen, se definió un modelo con tipado explícito y formatos estrictos:
* **transaction_id (String):** Extraído de `id`, `transaction_id` o `ref`.
* **amount (Float):** Estandarizado con punto decimal.
* **currency (String):** Código ISO 4217 de 3 letras en mayúsculas (USD, EUR).
* **timestamp (String):** Formato unificado corporativo `YYYY-MM-DD HH:MM:SS`.
* **status (String):** Estado canónico mapeado (`COMPLETED`, `PENDING`, `FAILED`).
* **source (String):** Origen determinado dinámicamente (`Fuente_A`, `Fuente_B`, `Fuente_C`).

### 2. Reglas Explícitas de Normalización Aplicadas en el Código
* **Conversión Financiera (Fuente B):** Multiplicador de escala corregido. Dado que venía expresado en centavos enteros (`10050`), la lógica realiza una división exacta entre `100.0` para recuperar el flotante preciso (`100.50`).
* **Limpieza de Cadenas (Fuente C):** Remoción de caracteres especiales y símbolos de divisa (`€`), transformando la coma decimal europea (`,`) en punto (`.`) para permitir la conversión segura a flotante.
* **Inferencia de Divisa:** Ante la ausencia de campo de moneda en la Fuente C, el motor inspecciona el token del monto para asignar de forma determinista la moneda `EUR`.
* **Mapeo Semántico:** Los estados `completed`, `OK` y `success` se consolidan automáticamente bajo el estado homogéneo `COMPLETED`.

### 3. Política de Cuarentena (Validación y Métricas)
El sistema rechaza registros incompletos o sin identificador válido y los aísla en una lista de transacciones inválidas con un mensaje claro que explica el motivo de la falla (ej. *ID faltante* o *Monto inválido*), manteniendo la ejecución del programa intacta y garantizando auditorías transparentes.

---

## 🖥️ Interfaz de Línea de Comandos (CLI)
Al iniciar, la interfaz interactiva (CLI) cargará los datos, aplicará la matriz de transformación y desplegará un menú dinámico como el siguiente:

```text
==================================================
 SISTEMA DE NORMALIZACIÓN DE TRANSACCIONES
 MULTI-FUENTE
==================================================
1. Ver Resumen General de Métricas
2. Listar Transacciones Normalizadas (Válidas)
3. Filtrar Transacciones por Moneda o Estado
4. Ver Transacciones Rechazadas / Inválidas
5. Salir
==================================================
Seleccione una opción (1-5):

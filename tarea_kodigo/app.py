import json
import os
from datetime import datetime
import re

# ==========================================
# 1. CONFIGURACIÓN Y REGLAS DE NORMALIZACIÓN
# ==========================================
CONFIG = {
    "monedas_soportadas": {
        "USD": "USD",
        "EUR": "EUR",
        "EUR_SYMBOL": "€"
    },
    "mapeo_estados": {
        "completed": "COMPLETED",
        "ok": "COMPLETED",
        "success": "COMPLETED",
        "pending": "PENDING",
        "failed": "FAILED"
    },
    "formato_fecha_salida": "%Y-%m-%d %H:%M:%S"
}

# ==========================================
# 2. CAPA DE NORMALIZACIÓN Y VALIDACIÓN
# ==========================================
class DataNormalizer:
    @staticmethod
    def detectar_fuente(tx):
        if "id" in tx and "amount" in tx and "currency" in tx:
            return "Fuente_A"
        elif "transaction_id" in tx and "total" in tx and "currency_code" in tx:
            return "Fuente_B"
        elif "ref" in tx and "amount" in tx and "date" in tx:
            return "Fuente_C"
        return "Desconocida"

    @staticmethod
    def limpiar_monto(monto_raw, fuente, moneda_contexto=None):
        if monto_raw is None:
            return None
        try:
            if isinstance(monto_raw, (int, float)):
                if fuente == "Fuente_B":
                    return float(monto_raw) / 100.0  # Centavos a unidades
                return float(monto_raw)
            
            s = str(monto_raw).strip()
            # Limpieza para Fuente C (ej: €99,99)
            s = s.replace(CONFIG["monedas_soportadas"]["EUR_SYMBOL"], "")
            s = s.replace(",", ".")
            s = re.sub(r'[^0-9.]', '', s)
            return float(s)
        except Exception:
            return None

    @staticmethod
    def normalizar_moneda(moneda_raw, monto_raw=None):
        if not moneda_raw:
            if monto_raw and CONFIG["monedas_soportadas"]["EUR_SYMBOL"] in str(monto_raw):
                return "EUR"
            return "UNKNOWN"
        m = str(moneda_raw).strip().upper()
        if m in CONFIG["monedas_soportadas"]:
            return CONFIG["monedas_soportadas"][m]
        return m

    @staticmethod
    def normalizar_fecha(fecha_raw):
        if not fecha_raw:
            return None
        s = str(fecha_raw).strip()
        formatos = [
            "%Y-%m-%d %H:%M:%S",        # Fuente A: 2025-03-10 14:22:00
            "%d/%m/%Y %H:%M",           # Fuente B: 10/03/2025 14:22
            "%Y-%m-%dT%H:%M:%SZ",       # Fuente C: 2025-03-10T14:22:00Z
            "%Y-%m-%dT%H:%M:%S"
        ]
        for fmt in formatos:
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime(CONFIG["formato_fecha_salida"])
            except ValueError:
                continue
        return None

    @staticmethod
    def normalizar_estado(estado_raw):
        if not estado_raw:
            return "UNKNOWN"
        e = str(estado_raw).strip().lower()
        return CONFIG["mapeo_estados"].get(e, "UNKNOWN")

    def procesar_archivo(self, ruta_archivo):
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        validas = []
        invalidas = []
        
        for idx, tx in enumerate(datos):
            fuente = self.detectar_fuente(tx)
            
            if fuente == "Desconocida":
                invalidas.append({
                    "indice_original": idx,
                    "datos_raw": tx,
                    "motivo_rechazo": "Estructura/Fuente no reconocida"
                })
                continue
            
            # Extraer según fuente
            id_orig, monto_orig, moneda_orig, fecha_orig, estado_orig = None, None, None, None, None
            
            if fuente == "Fuente_A":
                id_orig = tx.get("id")
                monto_orig = tx.get("amount")
                moneda_orig = tx.get("currency")
                fecha_orig = tx.get("timestamp")
                estado_orig = tx.get("status")
            elif fuente == "Fuente_B":
                id_orig = tx.get("transaction_id")
                monto_orig = tx.get("total")
                moneda_orig = tx.get("currency_code")
                fecha_orig = tx.get("created_at")
                estado_orig = tx.get("state")
            elif fuente == "Fuente_C":
                id_orig = tx.get("ref")
                monto_orig = tx.get("amount")
                moneda_orig = "EUR" if CONFIG["monedas_soportadas"]["EUR_SYMBOL"] in str(monto_orig) else None
                fecha_orig = tx.get("date")
                estado_orig = tx.get("result")

            # Normalización
            monto_norm = self.limpiar_monto(monto_orig, fuente)
            moneda_norm = self.normalizar_moneda(moneda_orig, monto_orig)
            fecha_norm = self.normalizar_fecha(fecha_orig)
            estado_norm = self.normalizar_estado(estado_orig)

            # Criterio de Validación Estricta
            if id_orig is None or monto_norm is None or fecha_norm is None:
                motivos = []
                if id_orig is None: motivos.append("ID faltante")
                if monto_norm is None: motivos.append("Monto inválido/faltante")
                if fecha_norm is None: motivos.append("Fecha inválida/faltante")
                
                invalidas.append({
                    "indice_original": idx,
                    "datos_raw": tx,
                    "motivo_rechazo": ", ".join(motivos)
                })
            else:
                validas.append({
                    "transaction_id": str(id_orig),
                    "amount": monto_norm,
                    "currency": moneda_norm,
                    "timestamp": fecha_norm,
                    "status": estado_norm,
                    "source": fuente
                })
                
        return validas, invalidas

# ==========================================
# 3. CAPA DE MÉTRICAS Y AGREGACIONES
# ==========================================
class MetricsManager:
    @staticmethod
    def calcular(validas, invalidas):
        totales_por_moneda = {}
        conteo_por_estado = {}
        
        for tx in validas:
            moneda = tx["currency"]
            monto = tx["amount"]
            estado = tx["status"]
            
            totales_por_moneda[moneda] = totales_por_moneda.get(moneda, 0.0) + monto
            conteo_por_estado[estado] = conteo_por_estado.get(estado, 0) + 1
            
        return {
            "total_procesadas": len(validas) + len(invalidas),
            "total_validas": len(validas),
            "total_invalidas": len(invalidas),
            "conteo_por_estado": conteo_por_estado,
            "totales_por_moneda": totales_por_moneda
        }

# ==========================================
# 4. INTERFAZ DE USUARIO INTERACTIVA (CLI)
# ==========================================
class InteractiveCLI:
    def __init__(self, archivo_datos):
        self.archivo_datos = archivo_datos
        self.normalizer = DataNormalizer()
        self.validas = []
        self.invalidas = []
        self.metricas = {}

    def cargar_y_procesar(self):
        if not os.path.exists(self.archivo_datos):
            print(f"Error: El archivo {self.archivo_datos} no existe.")
            return False
        self.validas, self.invalidas = self.normalizer.procesar_archivo(self.archivo_datos)
        self.metricas = MetricsManager.calcular(self.validas, self.invalidas)
        return True

    def mostrar_menu(self):
        print("\n" + "="*50)
        print(" SISTEMA DE NORMALIZACIÓN DE TRANSACCIONES MULTI-FUENTE")
        print("="*50)
        print("1. Ver Resumen General de Métricas")
        print("2. Listar Transacciones Normalizadas (Válidas)")
        print("3. Filtrar Transacciones por Moneda o Estado")
        print("4. Ver Transacciones Rechazadas / Inválidas")
        print("5. Salir")
        print("="*50)

    def ejecutar(self):
        if not self.cargar_y_procesar():
            return
        
        while True:
            self.mostrar_menu()
            opcion = input("Seleccione una opción (1-5): ").strip()
            
            if opcion == "1":
                print("\n--- RESUMEN GENERAL DE MÉTRICAS ---")
                print(f"Total Registros Procesados: {self.metricas['total_procesadas']}")
                print(f"Registros Válidos:          {self.metricas['total_validas']}")
                print(f"Registros Inválidos:        {self.metricas['total_invalidas']}")
                print("\nConteo por Estado Normalizado:")
                for est, count in self.metricas['conteo_por_estado'].items():
                    print(f"  - {est}: {count}")
                print("\nVolumen Total por Moneda:")
                for mon, total in self.metricas['totales_por_moneda'].items():
                    print(f"  - {mon}: {total:,.2f}")
                    
            elif opcion == "2":
                print("\n--- TRANSACCIONES NORMALIZADAS VÁLIDAS ---")
                if not self.validas:
                    print("No hay transacciones válidas.")
                for tx in self.validas:
                    print(f"ID: {tx['transaction_id']} | {tx['timestamp']} | {tx['amount']:,.2f} {tx['currency']} | Estado: {tx['status']} | [{tx['source']}]")
                    
            elif opcion == "3":
                print("\n--- FILTRAR TRANSACCIONES ---")
                criterio = input("Ingrese el término de filtro (ej: USD, EUR, COMPLETED, Fuente_B): ").strip().upper()
                encontradas = [tx for tx in self.validas if 
                               criterio in tx['currency'].upper() or 
                               criterio in tx['status'].upper() or 
                               criterio in tx['source'].upper()]
                print(f"\nResultados para el filtro '{criterio}':")
                if not encontradas:
                    print("No se encontraron registros.")
                for tx in encontradas:
                    print(f"ID: {tx['transaction_id']} | {tx['timestamp']} | {tx['amount']:,.2f} {tx['currency']} | Estado: {tx['status']}")
                    
            elif opcion == "4":
                print("\n--- TRANSACCIONES RECHAZADAS E INCONSISTENCIAS ---")
                if not self.invalidas:
                    print("No se encontraron registros inválidos.")
                for tx in self.invalidas:
                    print(f"Índice: {tx['indice_original']} | Motivo: {tx['motivo_rechazo']} | Datos: {tx['datos_raw']}")
                    
            elif opcion == "5":
                print("\n¡Gracias por utilizar el sistema normalizador!")
                break
            else:
                print("\nOpción no válida. Intente de nuevo.")

if __name__ == "__main__":
    # Inicializa de forma automática con el archivo generado
    cli = InteractiveCLI("transactions.json")
    # Para la entrega del estudiante se ejecuta invocando cli.ejecutar()
    cli.ejecutar()

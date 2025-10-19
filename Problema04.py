# problema4_sunat.py
import requests
import sqlite3
from pymongo import MongoClient
from datetime import date, timedelta
import time
import sys

# CONFIGURACIÓN
API_BASE = "https://api.decolecta.com/v1/tipo-cambio/sunat"
USE_TOKEN = False              # True si vas a usar token
TOKEN = "tu_token_aqui"        # si es necesario
SQLITE_DB = "base.db"
SQLITE_TABLE = "sunat_info"
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "sunat_db"
MONGO_COLLECTION = "sunat_info"

# Función para obtener tipo de cambio para una fecha (YYYY-MM-DD)
def obtener_tipo_cambio_fecha(fecha_iso):
    params = {"date": fecha_iso}
    headers = {}
    if USE_TOKEN and TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    try:
        r = requests.get(API_BASE, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        # Estructura esperada: puede variar; buscamos keys típicas
        # Ejemplos de campos: 'compra'/'venta' o 'buy'/'sell' o 'tipo_cambio_compra'...
        # Normalizaremos:
        for key in ["compra", "buy", "purchase", "compra_sunat"]:
            if key in data:
                compra = float(data[key])
                break
        else:
            compra = None

        for key in ["venta", "sell", "sale", "venta_sunat"]:
            if key in data:
                venta = float(data[key])
                break
        else:
            venta = None

        # A veces la respuesta puede anidarse (ej: data['data'] o similar)
        if compra is None or venta is None:
            # intentar inspeccionar keys comunes dentro de l objeto
            if isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, dict):
                        for key in ["compra","venta","buy","sell"]:
                            if key in v:
                                compra = compra or (float(v.get("compra") or v.get("buy")) if v.get("compra") or v.get("buy") else compra)
                                venta = venta or (float(v.get("venta") or v.get("sell")) if v.get("venta") or v.get("sell") else venta)
        # Si aun no tenemos valores, devolver el json para debug
        return {"fecha": fecha_iso, "compra": compra, "venta": venta, "raw": data}
    except Exception as e:
        print(f"Error al consultar {fecha_iso}: {e}", file=sys.stderr)
        return {"fecha": fecha_iso, "compra": None, "venta": None, "raw": None}

# Crear/abrir sqlite y tabla
def crear_tabla_sqlite():
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {SQLITE_TABLE} (
            fecha TEXT PRIMARY KEY,
            compra REAL,
            venta REAL
        )
    """)
    conn.commit()
    return conn

# Insertar/actualizar en sqlite
def upsert_sqlite(conn, fecha, compra, venta):
    cur = conn.cursor()
    cur.execute(f"""
        INSERT INTO {SQLITE_TABLE} (fecha, compra, venta)
        VALUES (?, ?, ?)
        ON CONFLICT(fecha) DO UPDATE SET compra=excluded.compra, venta=excluded.venta
    """, (fecha, compra, venta))
    conn.commit()

# Insertar en MongoDB
def upsert_mongo(collection, doc):
    collection.update_one({"fecha": doc["fecha"]}, {"$set": doc}, upsert=True)

def main():
    # 1) Prepara sqlite y mongo
    conn = crear_tabla_sqlite()
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    col = db[MONGO_COLLECTION]

    # 2) Recorrer todas las fechas de 2023
    start = date(2023, 1, 1)
    end = date(2023, 12, 31)
    current = start
    delta = timedelta(days=1)
    contador = 0
    while current <= end:
        iso = current.isoformat()
        info = obtener_tipo_cambio_fecha(iso)
        compra = info.get("compra")
        venta = info.get("venta")

        # Si el API devuelve None por fines de semana o errores, puedes elegir:
        # - guardarlo como NULL (None)
        # - o intentar obtener la fecha anterior (no implementado por defecto)
        upsert_sqlite(conn, iso, compra, venta)
        # Guardar documento en mongo (almacenar raw para trazabilidad)
        doc = {"fecha": iso, "compra": compra, "venta": venta, "raw": info.get("raw")}
        upsert_mongo(col, doc)

        contador += 1
        # pequeña pausa para evitar sobrecarga
        time.sleep(0.1)
        current += delta

    print(f"Proceso terminado. {contador} días procesados y almacenados en sqlite y mongo.")

    # 3) Mostrar contenido de la tabla sqlite (ejemplo: mostrar primeras 20 filas)
    cur = conn.cursor()
    cur.execute(f"SELECT fecha, compra, venta FROM {SQLITE_TABLE} ORDER BY fecha LIMIT 20")
    rows = cur.fetchall()
    print("Primeras filas (fecha, compra, venta):")
    for r in rows:
        print(r)

    conn.close()
    client.close()

if __name__ == "__main__":
    main()

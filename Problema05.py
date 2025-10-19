# problema5_solarizar.py
import sqlite3
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import sys

# CONFIG
SQLITE_DB = "base.db"
SQLITE_TABLE = "sunat_info"
VENTAS_CSV = "ventas.csv"         # Ruta a tu archivo ventas
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "ventas_db"
MONGO_COLLECTION = "ventas_solarizadas"

def obtener_tipo_cambio_para_fecha(conn, fecha_iso):
    """Busca el tipo de cambio en sqlite para fecha exacta.
       Si no existe, intenta buscar el último día anterior con valor (backfill)."""
    cur = conn.cursor()
    cur.execute(f"SELECT compra, venta FROM {SQLITE_TABLE} WHERE fecha = ?", (fecha_iso,))
    row = cur.fetchone()
    if row and (row[0] is not None or row[1] is not None):
        return row[0], row[1]
    # Backfill: buscar el último registro anterior con datos
    cur.execute(f"SELECT fecha, compra, venta FROM {SQLITE_TABLE} WHERE fecha < ? AND (compra IS NOT NULL OR venta IS NOT NULL) ORDER BY fecha DESC LIMIT 1", (fecha_iso,))
    row2 = cur.fetchone()
    if row2:
        return row2[1], row2[2]
    return None, None

def main():
    # 1) Leer ventas.csv (intentar detectar columnas)
    try:
        df = pd.read_csv(VENTAS_CSV, parse_dates=["fecha"], dayfirst=False)
    except Exception as e:
        print(f"Error leyendo {VENTAS_CSV}: {e}", file=sys.stderr)
        return

    # Normalizar nombres de columnas
    cols = [c.lower() for c in df.columns]
    mapping = {}
    # detectar fecha
    for c in df.columns:
        if c.lower() in ["fecha","date","día","dia"]:
            mapping["fecha"] = c
        if c.lower() in ["producto","producto_name","item","product","nombre"]:
            mapping["producto"] = c
        if c.lower() in ["precio","price","valor"]:
            mapping["precio"] = c
        if c.lower() in ["cantidad","qty","cantidad_vendida","units"]:
            mapping["cantidad"] = c

    # Verificar que tengamos al menos fecha, producto y precio
    if "fecha" not in mapping or "producto" not in mapping or "precio" not in mapping:
        print("El CSV debe contener al menos columnas de fecha, producto y precio. Ajusta nombres o edita el script.", file=sys.stderr)
        print("Columnas detectadas:", df.columns.tolist(), file=sys.stderr)
        return

    # Si no hay cantidad asumimos 1
    if "cantidad" not in mapping:
        df["cantidad"] = 1
        mapping["cantidad"] = "cantidad"

    # 2) Conectar a sqlite para leer tipo de cambio
    conn = sqlite3.connect(SQLITE_DB)

    # 3) Para cada fila, obtener tipo de cambio según fecha y calcular precio_soles = precio_usd * venta (o compra)
    #    Usaremos 'venta' (precio de venta del dólar en PEN) para convertir USD->PEN.
    df["fecha_str"] = df[mapping["fecha"]].dt.date.astype(str)
    compras = []
    ventas = []
    precios_soles = []
    problemas = 0
    for idx, row in df.iterrows():
        fecha_iso = row["fecha_str"]
        compra, venta = obtener_tipo_cambio_para_fecha(conn, fecha_iso)
        if venta is None and compra is None:
            # No hay tipo de cambio disponible
            compras.append(None)
            ventas.append(None)
            precios_soles.append(None)
            problemas += 1
            continue
        compras.append(compra)
        ventas.append(venta)
        precio_usd = float(row[mapping["precio"]])
        cantidad = float(row[mapping["cantidad"]])
        # Convertir USD a PEN. Usar 'venta' para convertir (USD * venta PEN/USD)
        precio_soles = precio_usd * cantidad * venta
        precios_soles.append(precio_soles)

    df["tipo_cambio_compra"] = compras
    df["tipo_cambio_venta"] = ventas
    df["precio_soles_total"] = precios_soles

    # 4) Total vendido (solarizado) por producto
    resumen = df.groupby(mapping["producto"])["precio_soles_total"].sum().reset_index()
    resumen = resumen.rename(columns={mapping["producto"]: "producto", "precio_soles_total": "total_soles_vendido"})

    # 5) Guardar resumen en MongoDB
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    col = db[MONGO_COLLECTION]

    # Insertar documentos por producto (reemplazar si ya existe)
    for _, r in resumen.iterrows():
        doc = {
            "producto": r["producto"],
            "total_soles_vendido": float(r["total_soles_vendido"]) if pd.notnull(r["total_soles_vendido"]) else None,
            "origen": "calculo_solarizado_ventas_csv"
        }
        col.update_one({"producto": doc["producto"]}, {"$set": doc}, upsert=True)

    # 6) Informar resultado resumen
    print("Resumen total vendido por producto (Soles):")
    print(resumen.to_string(index=False))

    if problemas > 0:
        print(f"Hubo {problemas} filas sin tipo de cambio disponible; sus totales quedaron como NULL.")

    conn.close()
    client.close()

if __name__ == "__main__":
    main()

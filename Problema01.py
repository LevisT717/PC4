# Nombre de los archivos
entrada = "temperaturas.txt"
salida = "resumen_temperaturas.txt"

# Listas para almacenar datos
temperaturas = []

with open(entrada, "r", encoding="utf-8") as f:
    for linea in f:
        # Eliminar espacios y saltos de línea
        linea = linea.strip()
        if linea:  # Evitar líneas vacías
            fecha, temp = linea.split(",")  # Separar por coma
            temperaturas.append(float(temp))  # Guardar temperatura como número


promedio = sum(temperaturas) / len(temperaturas)
maxima = max(temperaturas)
minima = min(temperaturas)


with open(salida, "w", encoding="utf-8") as f:
    f.write("Resumen de Temperaturas\n")
    f.write("=======================\n")
    f.write(f"Temperatura promedio: {promedio:.2f}°C\n")
    f.write(f"Temperatura máxima: {maxima:.2f}°C\n")
    f.write(f"Temperatura mínima: {minima:.2f}°C\n")

print("Archivo 'resumen_temperaturas.txt' creado correctamente.")
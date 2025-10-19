# --- Programa: Contador de líneas de código (LOC) en un archivo Python ---

def contar_lineas_codigo(ruta_archivo):
    """Cuenta las líneas de código en un archivo .py, excluyendo comentarios y líneas vacías."""
    try:
        # Validar que el archivo tenga extensión .py
        if not ruta_archivo.endswith(".py"):
            print("El archivo debe tener extensión '.py'.")
            return
        
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        
        contador = 0
        
        for linea in lineas:
            # Quitar espacios al inicio y final
            linea = linea.strip()
            
            # Ignorar líneas vacías o comentarios (que inician con "#")
            if linea == "" or linea.startswith("#"):
                continue
            
            # Contar solo las líneas que son código real
            contador += 1
        
        print(f"El archivo '{ruta_archivo}' contiene {contador} líneas de código.")
    
    except FileNotFoundError:
        print("No se encontró el archivo. Verifique la ruta e inténtelo nuevamente.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")


# --- Programa principal ---
def main():
    ruta = input("Ingrese la ruta completa del archivo .py: ").strip()
    contar_lineas_codigo(ruta)


if __name__ == "__main__":
    main()

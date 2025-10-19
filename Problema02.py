def crear_tabla():
    """Solicita un número y guarda su tabla de multiplicar en un archivo."""
    try:
        n = int(input("Ingrese un número entero entre 1 y 10: "))
        if n < 1 or n > 10:
            print("El número debe estar entre 1 y 10.")
            return
        
        nombre_archivo = f"tabla-{n}.txt"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            for i in range(1, 11):
                f.write(f"{n} x {i} = {n * i}\n")
        
        print(f"Tabla del {n} guardada en '{nombre_archivo}'.")
    
    except ValueError:
        print("Debe ingresar un número entero.")


def leer_tabla():
    """Lee y muestra la tabla completa desde un archivo existente."""
    try:
        n = int(input("Ingrese el número de la tabla que desea leer (1-10): "))
        nombre_archivo = f"tabla-{n}.txt"
        
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            print(f"\n Contenido de '{nombre_archivo}':\n")
            print(f.read())
    
    except FileNotFoundError:
        print(f"El archivo 'tabla-{n}.txt' no existe. Primero debe crearlo.")
    except ValueError:
        print("Debe ingresar un número entero.")


def leer_linea_tabla():
    """Lee una línea específica de una tabla de multiplicar."""
    try:
        n = int(input("Ingrese el número de la tabla (1-10): "))
        m = int(input("Ingrese el número de línea que desea ver (1-10): "))
        
        nombre_archivo = f"tabla-{n}.txt"
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()
            
            if m < 1 or m > len(lineas):
                print("El número de línea está fuera del rango (1-10).")
                return
            
            print(f"\nLínea {m} de la tabla del {n}:")
            print(lineas[m - 1].strip())
    
    except FileNotFoundError:
        print(f"El archivo 'tabla-{n}.txt' no existe. Primero debe crearlo.")
    except ValueError:
        print("Debe ingresar números enteros.")


# --- Menú principal ---
def menu():
    while True:
        print("\n=== MENÚ TABLAS DE MULTIPLICAR ===")
        print("1. Crear y guardar tabla")
        print("2. Leer una tabla completa")
        print("3. Mostrar una línea específica de una tabla")
        print("4. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            crear_tabla()
        elif opcion == "2":
            leer_tabla()
        elif opcion == "3":
            leer_linea_tabla()
        elif opcion == "4":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

# --- Ejecutar programa ---
if __name__ == "__main__":
    menu()

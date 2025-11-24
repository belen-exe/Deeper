from runtime.excepciones import DeeperError

def leer_archivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise DeeperError(f"No se encontró el archivo: {ruta}")
    except Exception as e:
        raise DeeperError(f"Error al leer archivo: {e}")


def escribir_archivo(nombre, contenido):
    try:
        with open(nombre, "w") as f:
            f.write(contenido)
        return True   # << correcto
    except Exception as e:
        print("ERROR: Error al escribir archivo:", e)
        return False


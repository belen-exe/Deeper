from runtime.excepciones import DeeperError
from librerias.StanMath import StanMath

def normalizar_valor(v):
    # booleanos
    if v is True:
        return "verdadero"
    if v is False:
        return "falso"

    # None
    if v is None:
        return "nulo"

    # número o string
    if isinstance(v, (int, float, str)):
        return str(v)

    # lista simple o matriz
    if isinstance(v, list):
        elementos = []
        for x in v:
            elementos.append(normalizar_valor(x))
        return "[" + ", ".join(elementos) + "]"

    # diccionario
    if isinstance(v, dict):
        elementos = []
        for k, val in v.items():
            elementos.append(f'"{k}": {normalizar_valor(val)}')
        return "{" + ", ".join(elementos) + "}"

    # fallback
    return str(v)


def builtin_mostrar(*args):
    valores = [normalizar_valor(a) for a in args]
    print(*valores)

# convierte a string
def a_cadena(valor):
    return str(valor)



BUILTINS = {
    # Output
    "mostrar": builtin_mostrar,
    "a_cadena": a_cadena,

    # Básicos
    "abs": StanMath.abs,
    "truncar": StanMath.truncar,

    # Aritmética
    "elevado": StanMath.elevado,
    "exp": StanMath.exp,
    "log": StanMath.log,
    "log10": StanMath.log10,
    "log2": StanMath.log2,
    "raiz": StanMath.raiz,

    # Trigonometría
    "sin": StanMath.sin,
    "cos": StanMath.cos,
    "tan": StanMath.tan,

    # Trigonometría inversa
    "asin": StanMath.asin,
    "acos": StanMath.acos,
    "atan": StanMath.atan,

    # Conversión ángulos
    "grados": StanMath.grados,
    "radianes": StanMath.radianes,

    # Combinatoria
    "factorial": StanMath.factorial,
    "comb": StanMath.comb,
    "perm": StanMath.perm,

    # Mínimo y máximo
    "min": StanMath.min,
    "max": StanMath.max,

    # Módulo
    "mod": StanMath.mod
}

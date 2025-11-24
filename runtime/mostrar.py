from runtime.excepciones import DeeperError

def normalizar_valor(v):
    # Normalizar booleanos
    if v is True:
        return "verdadero"
    if v is False:
        return "falso"

    # Normalizar listas, matrices, diccionarios recursivamente
    if isinstance(v, list):
        return "[" + ", ".join(normalizar_valor(x) for x in v) + "]"
    if isinstance(v, dict):
        partes = []
        for k, val in v.items():
            partes.append(f'"{k}": {normalizar_valor(val)}')
        return "{" + ", ".join(partes) + "}"

    return v


def builtin_mostrar(*args):
    valores = [normalizar_valor(a) for a in args]
    print(*valores)


BUILTINS = {
    "mostrar": builtin_mostrar
}

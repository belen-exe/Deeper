from runtime.excepciones import DeeperError

def builtin_mostrar(*args):
    print(*args)

BUILTINS = {
    "mostrar": builtin_mostrar
}

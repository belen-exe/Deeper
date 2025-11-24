# repl.py
import readline   # habilita historial con ↑
from antlr4 import InputStream, CommonTokenStream
from generacion.DeeperLexer import DeeperLexer
from generacion.DeeperParser import DeeperParser
from visitor.ejecutar import MiVisitor
from runtime.excepciones import DeeperError

def ejecutar_codigo(codigo, visitor):
    try:
        input_stream = InputStream(codigo)
        lexer = DeeperLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = DeeperParser(tokens)

        parser.removeErrorListeners()
        # podrías agregar tu listener si quieres
        tree = parser.programa()

        return visitor.visit(tree)

    except DeeperError as e:
        print("ERROR:", e)
    except Exception as e:
        print("Error inesperado:", e)

def repl():
    print("DEEPER — escribe 'salir' para terminar\n")

    visitor = MiVisitor()

    while True:
        try:
            linea = input(">>> ")

            if linea.strip() in ("salir", "exit", "chao"):
                break

            codigo = linea.strip()

            # Si no termina en ';' y no es algo tipo "entero x = 5"
            if not codigo.endswith(";"):

                # Es una expresión si contiene operadores, números o IDs
                # y NO contiene palabras clave de sentencia
                keywords = ["si", "mientras", "por", "fun", "retornar",
                            "entero", "decimal", "bool", "cadena",
                            "lista", "diccionario", "matriz"]

                if not any(codigo.startswith(kw) for kw in keywords):
                    codigo = f"mostrar({codigo});"

            ejecutar_codigo(codigo, visitor)


        except EOFError:
            break

if __name__ == "__main__":
    repl()

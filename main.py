from antlr4 import FileStream, CommonTokenStream
from antlr4.error.ErrorListener import ErrorListener
from generacion.DeeperLexer import DeeperLexer
from generacion.DeeperParser import DeeperParser
from visitor.ejecutar import MiVisitor
from runtime.excepciones import DeeperError

class ThrowingErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):

        texto = offendingSymbol.text

        # error lista nombre =[]
        if texto == '=':
            raise DeeperError(
                "Asignación inválida. Falta el tipo antes del nombre.",
                linea=line,
                columna=column
            )

        # Identificador inesperado
        if texto == 'lista':
            raise DeeperError(
                "Error: no puedes iniciar una sentencia solo con 'lista'. "
                "Debes usar: lista nombre = [...];",
                linea=line,
                columna=column
            )

        # Error sintáctico genérico
        raise DeeperError(f"Error sintáctico: {msg}", linea=line, columna=column)


def ejecutar_archivo(ruta):
    input_stream = FileStream(ruta, encoding='utf-8')
    
    lexer = DeeperLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    
    parser = DeeperParser(tokens)

    # listener
    parser.removeErrorListeners()
    parser.addErrorListener(ThrowingErrorListener())

    tree = parser.programa()

    visitor = MiVisitor()

    try:
        visitor.visit(tree)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("uso: python main.py archivo.dp")
    else:
        try:
            ejecutar_archivo(sys.argv[1])
        except DeeperError as e:
            print("ERROR:", e)

class DeeperError(Exception):
    def __init__(self, mensaje, linea=None, columna=None):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        super().__init__(self.__str__())

    def __str__(self):
        if self.linea is not None:
            return f"[Linea {self.linea}, Col {self.columna}] {self.mensaje}"
        return self.mensaje


class RetornarValor(Exception):
    #Excepcion interna para controlar 'retornar' dentro de funciones.
    def __init__(self, valor):
        self.valor = valor

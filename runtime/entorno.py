class Entorno:
    def __init__(self, padre=None):
        self.padre = padre
        self.tabla = {}

    def definir(self, nombre, valor):
        self.tabla[nombre] = valor

    def asignar(self, nombre, valor):
        if nombre in self.tabla:
            self.tabla[nombre] = valor
        elif self.padre:
            self.padre.asignar(nombre, valor)
        else:
            raise Exception(f"Variable '{nombre}' no definida.")

    def obtener(self, nombre):
        if nombre in self.tabla:
            return self.tabla[nombre]
        if self.padre:
            return self.padre.obtener(nombre)
        raise Exception(f"Variable '{nombre}' no definida.")

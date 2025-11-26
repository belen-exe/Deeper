from librerias.StanPlot import DeeperPlotInterpreter
from generacion.DeeperParserVisitor import DeeperParserVisitor
from runtime.excepciones import DeeperError, RetornarValor
from runtime.retorno import Entorno
from runtime.mostrar import BUILTINS
from librerias.archivos import leer_archivo, escribir_archivo
from librerias.StanRegression import regresion_pendiente, regresion_intercepto, predecir

class FuncionDefinida:
    def __init__(self, nombre, parametros, cuerpo, entorno_def):
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo
        self.entorno_def = entorno_def


class MiVisitor(DeeperParserVisitor):

    def __init__(self):
        # entorno global
        self.global_entorno = Entorno()

        # stack de entornos, iniciamos con el global
        self.entornos = [self.global_entorno]

        # registrar funciones builtin
        for nombre, fun in BUILTINS.items():
            self.global_entorno.definir(nombre, fun)

        self.global_entorno.definir("leer_archivo", leer_archivo)
        self.global_entorno.definir("escribir_archivo", escribir_archivo)
                # >>> Registrar funciones de graficación <<<
        plot = DeeperPlotInterpreter()  # instancia

        self.global_entorno.definir("crear_lineas", plot.crear_lineas)
        self.global_entorno.definir("crear_barras", plot.crear_barras)
        self.global_entorno.definir("crear_dispersion", plot.crear_dispersion)
        self.global_entorno.definir("crear_pastel", plot.crear_pastel)
        self.global_entorno.definir("crear_histograma", plot.crear_histograma)
        self.global_entorno.definir("crear_area", plot.crear_area)

        self.global_entorno.definir("color_linea", plot.color_linea)
        self.global_entorno.definir("color_puntos", plot.color_puntos)
        self.global_entorno.definir("color_barras", plot.color_barras)
        self.global_entorno.definir("color_fondo", plot.color_fondo)

        self.global_entorno.definir("titulo", plot.titulo)
        self.global_entorno.definir("guardar", plot.guardar)

        self.global_entorno.definir("regresion_pendiente", regresion_pendiente)
        self.global_entorno.definir("regresion_intercepto", regresion_intercepto)
        self.global_entorno.definir("predecir", predecir)

    def entorno_actual(self):
        """Retorna el entorno de la capa actual."""
        return self.entornos[-1]

    # programa
    def visitPrograma(self, ctx):
        for instr in ctx.instruccion():
            self.visit(instr)

    # declaraciones
    def visitDeclaracion_variable(self, ctx):
        nombre = ctx.ID().getText()
        valor = self.visit(ctx.expr()) if ctx.expr() else None
        self.entorno_actual().definir(nombre, valor)
        return valor

    def visitAsignacion(self, ctx):
        nombre = ctx.ID().getText()
        valor = self.visit(ctx.expr())
        self.entorno_actual().asignar(nombre, valor)
        return valor

    # funciones
    def visitDefinicion_funcion(self, ctx):
        nombre = ctx.ID().getText()
        params = [p.getText() for p in ctx.parametros().ID()] if ctx.parametros() else []
        funcion = FuncionDefinida(nombre, params, ctx, self.entorno_actual())
        self.global_entorno.definir(nombre, funcion)

    def ejecutar_funcion(self, f, args):
        if len(args) != len(f.parametros):
            raise DeeperError(f"La función '{f.nombre}' esperaba {len(f.parametros)} argumentos.")

        # crear ambiente local con el entorno donde se definió
        entorno_local = Entorno(f.entorno_def)

        self.entornos.append(entorno_local)

        for param, valor in zip(f.parametros, args):
            entorno_local.definir(param, valor)

        # ejecutar cuerpo
        try:
            for instr in f.cuerpo.instruccion():
                self.visit(instr)
        except RetornarValor as r:
            self.entornos.pop()
            return r.valor

        self.entornos.pop()
        return None

    def visitLlamada_funcion(self, ctx):
        nombre = ctx.ID().getText()        # aquí SÍ debe existir ID
        args = []

        if ctx.argumentos():
            args = [self.visit(e) for e in ctx.argumentos().expr()]

        fun = self.entorno_actual().obtener(nombre)

        # Si tu lenguaje tiene funciones definidas por el usuario:
        if isinstance(fun, FuncionDefinida):
            return self._invocar_funcion_definida(fun, args)

        if callable(fun):
            return fun(*args)

        raise DeeperError(f"'{nombre}' no es una función")

    # SI/SINO
    def visitCondicion(self, ctx):
        cond = self.visit(ctx.expr())
        instrucciones = ctx.instruccion()

        # sin SINO
        if not ctx.SINO():
            if cond:
                for instr in instrucciones:
                    self.visit(instr)
            return

        pos_sino = ctx.SINO().getSymbol().start
        bloque_si = []
        bloque_sino = []

        for instr in instrucciones:
            if instr.start.start < pos_sino:
                bloque_si.append(instr)
            else:
                bloque_sino.append(instr)

        if cond:
            for instr in bloque_si:
                self.visit(instr)
        else:
            for instr in bloque_sino:
                self.visit(instr)

    # mientras
    def visitBucle_mientras(self, ctx):
        while self.visit(ctx.expr()):
            for instr in ctx.instruccion():
                self.visit(instr)

    # BUCLE POR x EN y
    def visitBucle_por(self, ctx):
        var = ctx.ID().getText()
        iterable = self.visit(ctx.expr())

        if not hasattr(iterable, "__iter__"):
            raise DeeperError(f"'{iterable}' no es iterable.")

        for valor in iterable:
            self.entorno_actual().definir(var, valor)
            for instr in ctx.instruccion():
                self.visit(instr)

    # ESTRUCTURAS: LISTA / DICCIONARIO / MATRIZ
    def visitLista(self, ctx):
        exprs = ctx.expr()
        if not exprs:
            return []
        return [self.visit(e) for e in exprs]

    def visitClave_valor(self, ctx):
        clave = ctx.STRING().getText().strip('"')
        valor = self.visit(ctx.expr())
        return clave, valor

    def visitDiccionario(self, ctx):
        kvs = ctx.clave_valor()
        if not kvs:
            return {}
        resultado = {}
        for kv in kvs:
            clave, valor = self.visit(kv)
            resultado[clave] = valor
        return resultado

    def visitMatriz(self, ctx):
        listas = ctx.lista()
        return [self.visit(l) for l in listas]


    # RETURN
    def visitRetornar(self, ctx):
        valor = self.visit(ctx.expr())
        raise RetornarValor(valor)

    # EXPRESIONES
    def visitExpr(self, ctx):
        return self.visit(ctx.orExpr())

    def visitOrExpr(self, ctx):
        res = self.visit(ctx.andExpr(0))
        for i in range(1, len(ctx.andExpr())):
            res = res or self.visit(ctx.andExpr(i))
        return res

    def visitAndExpr(self, ctx):
        res = self.visit(ctx.eqExpr(0))
        for i in range(1, len(ctx.eqExpr())):
            res = res and self.visit(ctx.eqExpr(i))
        return res

    def visitEqExpr(self, ctx):
        left = self.visit(ctx.relExpr(0))
        rels = ctx.relExpr()
        ops = [c.getText() for c in ctx.children if c.getText() in ("==", "!=")]

        for i, op in enumerate(ops):
            right = self.visit(rels[i + 1])
            left = (left == right) if op == "==" else (left != right)
        return left

    def visitRelExpr(self, ctx):
        left = self.visit(ctx.addExpr(0))
        adds = ctx.addExpr()
        ops = [c.getText() for c in ctx.children if c.getText() in ("<", ">", "<=", ">=")]

        for i, op in enumerate(ops):
            right = self.visit(adds[i + 1])
            if op == "<":
                left = left < right
            elif op == ">":
                left = left > right
            elif op == "<=":
                left = left <= right
            elif op == ">=":
                left = left >= right
        return left

    def visitAddExpr(self, ctx):
        left = self.visit(ctx.mulExpr(0))
        muls = ctx.mulExpr()
        ops = [c.getText() for c in ctx.children if c.getText() in ("+", "-")]

        for i, op in enumerate(ops):
            right = self.visit(muls[i + 1])
            left = left + right if op == "+" else left - right
        return left

    def visitMulExpr(self, ctx):
        left = self.visit(ctx.unaryExpr(0))
        uns = ctx.unaryExpr()
        ops = [c.getText() for c in ctx.children if c.getText() in ("*", "/", "%")]

        for i, op in enumerate(ops):
            right = self.visit(uns[i + 1])
            if op == "*":
                left *= right
            elif op == "/":
                left /= right
            else:
                left %= right
        return left

    def visitUnaryExpr(self, ctx):
        if ctx.NOT():
            return not self.visit(ctx.unaryExpr())
        if ctx.MINUS():
            return -self.visit(ctx.unaryExpr())
        return self.visit(ctx.atom())

    def visitAtom(self, ctx):
        # 1. Evaluar el 'primary': ID, literal, (expr), lista, etc.
        valor = self.visit(ctx.primary())

        # 2. Aplicar los sufijos en orden: .prop, .metodo(...), [idx], etc.
        for suf in ctx.atomSuffix():
            # ------- Acceso / método con punto -------
            if suf.DOT():
                call = suf.llamada_funcion()

                if call is not None:
                    # caso: obj.metodo(...)
                    # aquí el nombre está dentro de llamada_funcion: ID LPAREN ...
                    nombre = call.ID().getText()

                    args = []
                    if call.argumentos():
                        args = [self.visit(e) for e in call.argumentos().expr()]

                    try:
                        fun = getattr(valor, nombre)
                    except AttributeError:
                        raise DeeperError(f"El módulo/objeto no tiene la función '{nombre}'")

                    valor = fun(*args)

                else:
                    # caso: obj.prop   (atomSuffix: DOT ID)
                    nombre = suf.ID().getText()
                    try:
                        valor = getattr(valor, nombre)
                    except AttributeError:
                        raise DeeperError(f"El módulo/objeto no tiene '{nombre}'")

            # ------- Indexación obj[x] -------
            elif suf.LBRACK():
                idx = self.visit(suf.expr())
                try:
                    valor = valor[idx]
                except Exception:
                    raise DeeperError("Error al indexar el objeto")

        return valor



    
    def visitPrimary(self, ctx):
        if ctx.NUMBER():
            t = ctx.NUMBER().getText()
            return float(t) if '.' in t else int(t)

        if ctx.STRING():
            return ctx.STRING().getText().strip('"')

        if ctx.BOOL_LIT():
            return ctx.BOOL_LIT().getText() == "verdadero"

        if ctx.ID():
            return self.entorno_actual().obtener(ctx.ID().getText())

        if ctx.llamada_funcion():
            return self.visit(ctx.llamada_funcion())

        if ctx.lista():
            return self.visit(ctx.lista())

        if ctx.diccionario():
            return self.visit(ctx.diccionario())

        if ctx.matriz():
            return self.visit(ctx.matriz())

        # (expr)
        if ctx.expr():
            return self.visit(ctx.expr())

        raise DeeperError("Expresión primaria inválida.")
    
    #para librerias
    def visitImportar_stmt(self, ctx):
        modulo = ctx.ID(0).getText()
        alias = modulo

        # manejar 'importar StanMath como m;'
        if ctx.ID(1) is not None:
            alias = ctx.ID(1).getText()

        try:
            # Importa el módulo Python: librerias.StanMath, librerias.archivos, etc.
            py_module = __import__(f"librerias.{modulo}", fromlist=[modulo])
        except Exception:
            raise DeeperError(f"No se pudo cargar el módulo '{modulo}'.")

        # Si dentro del módulo existe un atributo con el mismo nombre que el módulo
        # (ej. en librerias/StanMath.py hay una clase StanMath),
        # usamos esa clase. Si no, usamos el módulo completo.
        obj = getattr(py_module, modulo, py_module)

        # Guardamos directamente el objeto (clase o módulo) bajo el alias.
        # Así, desde Deeper podrás hacer:
        #   importar StanMath;
        #   mostrar(StanMath.PI);
        self.entorno_actual().definir(alias, obj)


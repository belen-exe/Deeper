from generacion.DeeperParserVisitor import DeeperParserVisitor
from runtime.excepciones import DeeperError, RetornarValor
from runtime.retorno import Entorno
from runtime.mostrar import BUILTINS


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
        nombre = ctx.ID().getText()
        args = [self.visit(e) for e in ctx.argumentos().expr()] if ctx.argumentos() else []

        fun = self.entorno_actual().obtener(nombre)

        if callable(fun):
            return fun(*args)

        if isinstance(fun, FuncionDefinida):
            return self.ejecutar_funcion(fun, args)

        raise DeeperError(f"'{nombre}' no es una función válida.")

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
        if ctx.NUMBER():
            t = ctx.NUMBER().getText()
            return float(t) if "." in t else int(t)
        if ctx.STRING():
            return ctx.STRING().getText().strip('"')
        if ctx.BOOL_LIT():
            return ctx.BOOL_LIT().getText() == "verdadero"
        if ctx.ID():
            return self.entorno_actual().obtener(ctx.ID().getText())
        if ctx.LPAREN():
            return self.visit(ctx.expr())
        return self.visitChildren(ctx)

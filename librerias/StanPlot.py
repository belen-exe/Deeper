from librerias.StanMath import StanMath
from librerias.StanRegression import regresion_pendiente, regresion_intercepto, predecir

def _rgb_to_str(rgb):
    try:
        r, g, b = rgb
    except:
        r, g, b = 0, 0, 0
    return f"rgb({int(r)},{int(g)},{int(b)})"


def _fmt_num(x):
    try:
        return f"{x:.2f}"
    except:
        return str(x)

class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Canvas:
    def __init__(self, ancho=800, alto=600):
        self.ancho = ancho
        self.alto = alto
        self.elementos = []
        self.color_fondo = (255, 255, 255)
        self.grafica = None

    def agregar_elemento(self, frag):
        self.elementos.append(frag)

    def render_svg(self):
        w = int(self.ancho)
        h = int(self.alto)
        bg = f'<rect width="{w}" height="{h}" fill="{_rgb_to_str(self.color_fondo)}"/>'

        text_title = ""
        text_x = ""
        text_y = ""

        if self.grafica:
            if self.grafica.titulo:
                text_title = f'<text x="{w/2}" y="30" text-anchor="middle" font-size="20" font-family="Arial">{self.grafica.titulo}</text>'
            if self.grafica.etiqueta_x:
                text_x = f'<text x="{w/2}" y="{h-10}" text-anchor="middle" font-size="16" font-family="Arial">{self.grafica.etiqueta_x}</text>'
            if self.grafica.etiqueta_y:
                text_y = f'<text x="20" y="{h/2}" text-anchor="middle" font-size="16" font-family="Arial" transform="rotate(-90,20,{h/2})">{self.grafica.etiqueta_y}</text>'

        content = "\n".join(self.elementos)
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">\n{bg}\n{text_title}\n{text_x}\n{text_y}\n{content}\n</svg>'


class Grafica:
    def __init__(self, titulo="", etiqueta_x="", etiqueta_y=""):
        self.titulo = titulo
        self.etiqueta_x = etiqueta_x
        self.etiqueta_y = etiqueta_y
        self.canvas = Canvas()
        self.canvas.grafica = self
        self.datos = []
        self.color_linea = (0, 0, 0)
        self.color_barras = (0, 0, 0)
        self.color_puntos = (0, 0, 0)
        self.grosor = 2
        self.tamano_punto = 4
        self.min_x = 0
        self.max_x = 1
        self.min_y = 0
        self.max_y = 1

    def establecer_datos(self, datos):
        self.datos = datos

    def configurar_ejes(self, min_x, max_x, min_y, max_y):
        if max_x == min_x: max_x = min_x + 1
        if max_y == min_y: max_y = min_y + 1
        self.min_x = min_x; self.max_x = max_x
        self.min_y = min_y; self.max_y = max_y

    def escalar_punto(self, x, y):
        pad = 0.1
        w = float(self.canvas.ancho)
        h = float(self.canvas.alto)
        dx = (self.max_x - self.min_x) or 1
        dy = (self.max_y - self.min_y) or 1
        px = pad * w + ((x - self.min_x) / dx) * (w * (1 - 2 * pad))
        py = (1 - pad) * h - ((y - self.min_y) / dy) * (h * (1 - 2 * pad))
        return Punto(px, py)

def crear_grafica_lineas(xs, ys, titulo="", ex="", ey=""):
    g = Grafica(titulo, ex, ey)
    datos = list(zip(xs, ys))
    g.establecer_datos(datos)
    g.configurar_ejes(min(xs), max(xs), min(ys), max(ys))

    pts = [g.escalar_punto(x, y) for x, y in datos]
    stroke = _rgb_to_str(g.color_linea)
    sw = max(1, int(g.grosor))

    for i in range(len(pts) - 1):
        p1, p2 = pts[i], pts[i+1]
        g.canvas.agregar_elemento(f'<line x1="{_fmt_num(p1.x)}" y1="{_fmt_num(p1.y)}" x2="{_fmt_num(p2.x)}" y2="{_fmt_num(p2.y)}" stroke="{stroke}" stroke-width="{sw}" />')

    fill = _rgb_to_str(g.color_puntos)
    r = max(1, int(g.tamano_punto))
    for p in pts:
        g.canvas.agregar_elemento(f'<circle cx="{_fmt_num(p.x)}" cy="{_fmt_num(p.y)}" r="{r}" fill="{fill}" />')

    return g


def crear_grafica_dispersion(xs, ys, titulo="", ex="", ey=""):
    g = Grafica(titulo, ex, ey)
    datos = list(zip(xs, ys))
    g.establecer_datos(datos)
    g.configurar_ejes(min(xs), max(xs), min(ys), max(ys))

    fill = _rgb_to_str(g.color_puntos)
    r = max(1, int(g.tamano_punto))

    for x, y in datos:
        p = g.escalar_punto(x, y)
        g.canvas.agregar_elemento(f'<circle cx="{_fmt_num(p.x)}" cy="{_fmt_num(p.y)}" r="{r}" fill="{fill}" />')

    return g


def crear_grafica_barras(categorias, valores, titulo="", ex="", ey=""):
    g = Grafica(titulo, ex, ey)
    datos = list(enumerate(valores))
    g.establecer_datos(datos)
    g.configurar_ejes(-0.5, len(valores) - 0.5, 0, max(valores) if valores else 1)

    w = float(g.canvas.ancho)
    h = float(g.canvas.alto)
    total = len(valores)
    bar_width = (w * 0.7) / total if total > 0 else 10.0
    left0 = w * 0.15
    fill = _rgb_to_str(g.color_barras)

    for i, val in enumerate(valores):
        denom = (g.max_y - g.min_y) or 1.0
        rect_h = (val / denom) * (h * 0.6)
        x = left0 + i * (bar_width + 4)
        y = h * 0.8 - rect_h
        g.canvas.agregar_elemento(f'<rect x="{_fmt_num(x)}" y="{_fmt_num(y)}" width="{_fmt_num(bar_width)}" height="{_fmt_num(rect_h)}" fill="{fill}" />')

    return g


def guardar_grafica(grafica, ruta):
    svg = grafica.canvas.render_svg()
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(svg)

class DeeperPlotInterpreter:
    def __init__(self):
        self.current_graph = None

    def crear_regresion(self, xs, ys, titulo="", ex="", ey=""):
        m = regresion_pendiente(xs, ys)
        b = regresion_intercepto(xs, ys)
        pred = predecir(xs, m, b)

        # Primero puntos
        g = crear_grafica_dispersion(xs, ys, titulo, ex, ey)

        # Luego línea
        linea = crear_grafica_lineas(xs, pred, titulo, ex, ey)
        linea.canvas.color_fondo = g.canvas.color_fondo
        self.current_graph = linea
        return linea

    def crear_lineas(self, xs, ys, t="", ex="", ey=""):
        self.current_graph = crear_grafica_lineas(xs, ys, t, ex, ey)
        return self.current_graph

    def crear_barras(self, cat, val, t="", ex="", ey=""):
        self.current_graph = crear_grafica_barras(cat, val, t, ex, ey)
        return self.current_graph

    def crear_dispersion(self, xs, ys, t="", ex="", ey=""):
        self.current_graph = crear_grafica_dispersion(xs, ys, t, ex, ey)
        return self.current_graph

    def color_linea(self, r, g, b):
        if self.current_graph: self.current_graph.color_linea = (r, g, b)

    def color_puntos(self, r, g, b):
        if self.current_graph: self.current_graph.color_puntos = (r, g, b)

    def color_barras(self, r, g, b):
        if self.current_graph: self.current_graph.color_barras = (r, g, b)

    def tamano_puntos(self, t):
        if self.current_graph: self.current_graph.tamano_punto = int(t)

    def grosor_linea(self, g):
        if self.current_graph: self.current_graph.grosor = int(g)

    def color_fondo(self, r, g, b):
        if self.current_graph: self.current_graph.canvas.color_fondo = (r, g, b)

    def titulo(self, txt):
        if self.current_graph: self.current_graph.titulo = txt

    def guardar(self, ruta):
        if not self.current_graph: raise Exception("No hay gráfica para guardar")
        guardar_grafica(self.current_graph, ruta)

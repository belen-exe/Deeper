from librerias.StanMath import StanMath

# intentar importar StanRegression (debe existir)
try:
    from librerias.StanRegression import regresion_pendiente, regresion_intercepto, predecir
except Exception:
    # Si no existe, definimos placeholders que lanzan error si se usan.
    def regresion_pendiente(xs, ys):
        raise Exception("StanRegression no disponible.")
    def regresion_intercepto(xs, ys):
        raise Exception("StanRegression no disponible.")
    def predecir(xs, m, b):
        raise Exception("StanRegression no disponible.")

# ---------- utilidades ----------
def _rgb_to_str(rgb):
    try:
        r, g, b = rgb
    except Exception:
        r, g, b = 0, 0, 0
    return f"rgb({int(r)},{int(g)},{int(b)})"

def _fmt_num(x):
    try:
        # si es entero preservamos sin decimales
        if isinstance(x, int):
            return str(x)
        return f"{x:.2f}"
    except Exception:
        return str(x)

# ---------- primitivas ----------
class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Canvas:
    def __init__(self, ancho=800, alto=600):
        self.ancho = ancho
        self.alto = alto
        self.color_fondo = (255, 255, 255)
        self.grafica = None
        self.elementos = []

    def agregar_elemento(self, frag):
        self.elementos.append(frag)

    def render_svg(self):
        w = int(self.ancho)
        h = int(self.alto)
        bg = f'<rect width="{w}" height="{h}" fill="{_rgb_to_str(self.color_fondo)}"/>'

        # texto (título y etiquetas)
        text_title = ""
        text_x = ""
        text_y = ""
        if getattr(self, "grafica", None):
            g = self.grafica
            if getattr(g, "titulo", None):
                text_title = f'<text x="{w/2}" y="30" text-anchor="middle" font-size="20" font-family="Arial">{g.titulo}</text>'
            if getattr(g, "etiqueta_x", None):
                text_x = f'<text x="{w/2}" y="{h-10}" text-anchor="middle" font-size="14" font-family="Arial">{g.etiqueta_x}</text>'
            if getattr(g, "etiqueta_y", None):
                text_y = f'<text x="20" y="{h/2}" text-anchor="middle" font-size="14" font-family="Arial" transform="rotate(-90,20,{h/2})">{g.etiqueta_y}</text>'

        # ejes y ticks (si la grafica define ejes)
        ejes_svg = ""
        if getattr(self, "grafica", None):
            g = self.grafica
            mx = 60        # margen izquierdo
            my = 40        # margen superior/inferior
            xmin = getattr(g, "xmin", 0)
            xmax = getattr(g, "xmax", 1)
            ymin = getattr(g, "ymin", 0)
            ymax = getattr(g, "ymax", 1)

            # evita división por cero
            rango_x = (xmax - xmin) if (xmax - xmin) != 0 else 1.0
            rango_y = (ymax - ymin) if (ymax - ymin) != 0 else 1.0

            # eje X
            ejes_svg += f'<line x1="{mx}" y1="{h-my}" x2="{w-mx}" y2="{h-my}" stroke="black" stroke-width="1"/>\n'
            # eje Y
            ejes_svg += f'<line x1="{mx}" y1="{my}" x2="{mx}" y2="{h-my}" stroke="black" stroke-width="1"/>\n'

            pasos_x = 5
            for i in range(pasos_x + 1):
                valor = xmin + (rango_x / pasos_x) * i
                x = mx + ((valor - xmin) / rango_x) * (w - 2*mx)
                y = h - my
                ejes_svg += f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+6}" stroke="black" />'
                ejes_svg += f'<text x="{x}" y="{y+20}" font-size="10" text-anchor="middle">{_fmt_num(valor)}</text>\n'

            pasos_y = 5
            for i in range(pasos_y + 1):
                valor = ymin + (rango_y / pasos_y) * i
                x = mx
                y = h - my - ((valor - ymin) / rango_y) * (h - 2*my)
                ejes_svg += f'<line x1="{x}" y1="{y}" x2="{x-6}" y2="{y}" stroke="black" />'
                ejes_svg += f'<text x="{x-10}" y="{y+4}" font-size="10" text-anchor="end">{_fmt_num(valor)}</text>\n'

        content = "\n".join(self.elementos)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">\n{bg}\n{text_title}\n{text_x}\n{text_y}\n{ejes_svg}\n{content}\n</svg>'
        return svg

# ---------- Grafica ----------
class Grafica:
    def __init__(self, titulo="", etiqueta_x="", etiqueta_y=""):
        self.titulo = titulo
        self.etiqueta_x = etiqueta_x
        self.etiqueta_y = etiqueta_y
        self.canvas = Canvas()
        self.canvas.grafica = self
        self.datos = []
        # colores por defecto (Opción A: bonitos)
        self.color_linea = (200, 50, 50)
        self.color_puntos = (30, 90, 200)
        self.color_barras = (0, 140, 70)
        self.grosor = 2
        self.tamano_punto = 4
        # ejes virtuales
        self.xmin = 0
        self.xmax = 1
        self.ymin = 0
        self.ymax = 1

    def establecer_datos(self, datos):
        self.datos = datos

    def configurar_ejes(self, min_x, max_x, min_y, max_y):
        if max_x == min_x:
            max_x = min_x + 1
        if max_y == min_y:
            max_y = min_y + 1
        self.xmin = min_x
        self.xmax = max_x
        self.ymin = min_y
        self.ymax = max_y

    def escalar_punto(self, x, y):
        pad = 0.1
        w = float(self.canvas.ancho)
        h = float(self.canvas.alto)
        dx = (self.xmax - self.xmin) if (self.xmax - self.xmin) != 0 else 1.0
        dy = (self.ymax - self.ymin) if (self.ymax - self.ymin) != 0 else 1.0
        px = pad * w + ((x - self.xmin) / dx) * (w * (1.0 - 2.0 * pad))
        py = (1.0 - pad) * h - ((y - self.ymin) / dy) * (h * (1.0 - 2.0 * pad))
        return Punto(px, py)

# ---------- creadores ----------
def crear_grafica_lineas(xs, ys, titulo="", ex="", ey=""):
    if not xs: xs = [0]
    if not ys: ys = [0]
    g = Grafica(titulo, ex, ey)
    datos = list(zip(xs, ys))
    g.establecer_datos(datos)
    g.configurar_ejes(min(xs), max(xs), min(ys), max(ys))

    pts = [g.escalar_punto(x, y) for x, y in datos]
    stroke = _rgb_to_str(g.color_linea)
    sw = max(1, int(g.grosor))

    for i in range(len(pts) - 1):
        p1, p2 = pts[i], pts[i+1]
        g.canvas.agregar_elemento(f'<line x1="{_fmt_num(p1.x)}" y1="{_fmt_num(p1.y)}" x2="{_fmt_num(p2.x)}" y2="{_fmt_num(p2.y)}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" />')

    fill = _rgb_to_str(g.color_puntos)
    r = max(1, int(g.tamano_punto))
    for p in pts:
        g.canvas.agregar_elemento(f'<circle cx="{_fmt_num(p.x)}" cy="{_fmt_num(p.y)}" r="{r}" fill="{fill}" />')

    return g

def crear_grafica_dispersion(xs, ys, titulo="", ex="", ey=""):
    if not xs: xs = [0]
    if not ys: ys = [0]
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
    if not valores:
        valores = [0]
        categorias = categorias or []

    g = Grafica(titulo, ex, ey)
    datos = list(enumerate(valores))
    g.establecer_datos(datos)

    # ESCALAS: base real en 0 y margen superior mínimo
    min_x = -0.5
    max_x = len(valores) - 0.5 if valores else 0.5
    min_y = 0
    max_y = max(valores) * 1.05 if max(valores) != 0 else 1
    g.configurar_ejes(min_x, max_x, min_y, max_y)

    # Parámetros del canvas
    w = float(g.canvas.ancho)
    h = float(g.canvas.alto)
    mx = 60
    my = 40

    # Ancho de barras
    total = len(valores)
    bar_width = (w - 2*mx) / (total * 1.3)

    fill = _rgb_to_str(g.color_barras)

    for idx, val in enumerate(valores):
        # escalado usando la misma función de puntos (¡CORRECCIÓN!)
        p_bottom = g.escalar_punto(idx, 0)
        p_top = g.escalar_punto(idx, val)

        # dibujar barra
        x = p_bottom.x - bar_width/2
        y = p_top.y
        height = p_bottom.y - p_top.y

        g.canvas.agregar_elemento(
            f'<rect x="{_fmt_num(x)}" y="{_fmt_num(y)}" width="{_fmt_num(bar_width)}" height="{_fmt_num(height)}" fill="{fill}" />'
        )

        # === SOLO PONER CATEGORÍAS SI EL USUARIO LAS PASÓ ===
        if categorias and idx < len(categorias):
            label = categorias[idx]
            g.canvas.agregar_elemento(
                f'<text x="{_fmt_num(p_bottom.x)}" y="{_fmt_num(p_bottom.y + 14)}" font-size="10" text-anchor="middle">{label}</text>'
            )

        # valor encima (siempre mostrar)
        g.canvas.agregar_elemento(
            f'<text x="{_fmt_num(p_bottom.x)}" y="{_fmt_num(p_top.y - 6)}" font-size="10" text-anchor="middle">{_fmt_num(val)}</text>'
        )

    return g

def guardar_grafica(grafica, ruta):
    svg = grafica.canvas.render_svg()
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(svg)

# ---------- intérprete (instancia) ----------
class _StanPlotInterpreter:
    def __init__(self):
        self.current_graph = None

    def _apply_previous_styles(self, g):
        if self.current_graph:
            g.color_linea = self.current_graph.color_linea
            g.color_puntos = self.current_graph.color_puntos
            g.color_barras = self.current_graph.color_barras
            g.grosor = self.current_graph.grosor
            g.tamano_punto = self.current_graph.tamano_punto

    # API
    def crear_lineas(self, xs, ys, titulo="", ex="", ey=""):
        g = crear_grafica_lineas(xs, ys, titulo, ex, ey)
        self._apply_previous_styles(g)
        self.current_graph = g
        return g

    def crear_dispersion(self, xs, ys, titulo="", ex="", ey=""):
        g = crear_grafica_dispersion(xs, ys, titulo, ex, ey)
        self._apply_previous_styles(g)
        self.current_graph = g
        return g

    def crear_barras(self, categorias, valores, titulo="", ex="", ey=""):
        g = crear_grafica_barras(categorias, valores, titulo, ex, ey)
        self._apply_previous_styles(g)
        self.current_graph = g
        return g

    def crear_regresion(self, xs, ys, titulo="", ex="", ey=""):
        # puntos
        g_pts = crear_grafica_dispersion(xs, ys, titulo, ex, ey)
        # regresión con la librería StanRegression
        m = regresion_pendiente(xs, ys)
        b = regresion_intercepto(xs, ys)
        preds = predecir(xs, m, b)
        # línea de regresión
        g_line = crear_grafica_lineas(xs, preds, titulo, ex, ey)
        # ajustar estilos: línea roja por defecto, puntos azules
        g_line.color_linea = (200, 50, 50)
        g_pts.color_puntos = (30, 90, 200)
        # combinar: poner fragmentos de la línea encima del canvas de puntos
        for frag in g_line.canvas.elementos:
            g_pts.canvas.agregar_elemento(frag)
        # anotar ecuación (opcional) en la esquina superior izquierda
        try:
            eq = f"y = {_fmt_num(m)}x + {_fmt_num(b)}"
            g_pts.canvas.agregar_elemento(f'<text x="70" y="45" font-size="12" fill="black">{eq}</text>')
        except Exception:
            pass
        self._apply_previous_styles(g_pts)
        self.current_graph = g_pts
        return g_pts

    # estilos
    def color_linea(self, r, g, b):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.color_linea = (int(r), int(g), int(b))

    def color_puntos(self, r, g, b):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.color_puntos = (int(r), int(g), int(b))

    def color_barras(self, r, g, b):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.color_barras = (int(r), int(g), int(b))

    def tamano_puntos(self, t):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.tamano_punto = int(t)

    def grosor_linea(self, g):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.grosor = int(g)

    def color_fondo(self, r, g, b):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.canvas.color_fondo = (int(r), int(g), int(b))

    def titulo(self, txt):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.titulo = txt

    def guardar(self, ruta):
        if not self.current_graph:
            raise Exception("No hay gráfica para guardar")
        guardar_grafica(self.current_graph, ruta)

# instancia del módulo
StanPlot = _StanPlotInterpreter()

# funciones de módulo (para llamar como: StanPlot.crear_lineas(...) o desde Deeper usar StanPlot.crear_lineas)
def crear_lineas(xs, ys, titulo="", ex="", ey=""):
    return StanPlot.crear_lineas(xs, ys, titulo, ex, ey)

def crear_dispersion(xs, ys, titulo="", ex="", ey=""):
    return StanPlot.crear_dispersion(xs, ys, titulo, ex, ey)

def crear_barras(categorias, valores, titulo="", ex="", ey=""):
    return StanPlot.crear_barras(categorias, valores, titulo, ex, ey)

def crear_regresion(xs, ys, titulo="", ex="", ey=""):
    return StanPlot.crear_regresion(xs, ys, titulo, ex, ey)

def color_linea(r, g, b):
    return StanPlot.color_linea(r, g, b)

def color_puntos(r, g, b):
    return StanPlot.color_puntos(r, g, b)

def color_barras(r, g, b):
    return StanPlot.color_barras(r, g, b)

def tamano_puntos(t):
    return StanPlot.tamano_puntos(t)

def grosor_linea(g):
    return StanPlot.grosor_linea(g)

def color_fondo(r, g, b):
    return StanPlot.color_fondo(r, g, b)

def titulo(txt):
    return StanPlot.titulo(txt)

def guardar(ruta):
    return StanPlot.guardar(ruta)

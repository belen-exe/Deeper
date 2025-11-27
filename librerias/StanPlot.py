from librerias.StanMath import StanMath

# magia
def _rgb_to_str(rgb):
    # rgb es una tupla (r,g,b) con valores 0-255
    try:
        r, g, b = rgb
    except Exception:
        r, g, b = 0, 0, 0
    return f"rgb({int(r)},{int(g)},{int(b)})"

def _fmt_num(x):
    if isinstance(x, int):
        return str(x)
    try:
        return f"{x:.2f}"
    except Exception:
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

    def agregar_elemento(self, frag):
        self.elementos.append(frag)

    def render_svg(self, titulo="", eje_x="", eje_y="", min_x=None, max_x=None, min_y=None, max_y=None):
        w = int(self.ancho)
        h = int(self.alto)
        bg = f'<rect width="{w}" height="{h}" fill="{_rgb_to_str(self.color_fondo)}"/>'
        
        # Márgenes para las escalas
        pad = 0.1
        margen_izq = w * pad
        margen_der = w * (1 - pad)
        margen_sup = h * pad
        margen_inf = h * (1 - pad)
        
        # Agregar título si existe
        texto_svg = []
        if titulo:
            texto_svg.append(f'<text x="{w/2}" y="30" font-size="20" font-weight="bold" text-anchor="middle" fill="black">{titulo}</text>')
        
        # Agregar etiqueta eje X
        if eje_x:
            texto_svg.append(f'<text x="{w/2}" y="{h - 10}" font-size="14" text-anchor="middle" fill="black">{eje_x}</text>')
        
        # Agregar etiqueta eje Y (rotada)
        if eje_y:
            texto_svg.append(f'<text x="15" y="{h/2}" font-size="14" text-anchor="middle" fill="black" transform="rotate(-90, 15, {h/2})">{eje_y}</text>')
        
        # Dibujar ejes con líneas
        if min_x is not None and max_x is not None and min_y is not None and max_y is not None:
            # Línea eje X
            texto_svg.append(f'<line x1="{margen_izq}" y1="{margen_inf}" x2="{margen_der}" y2="{margen_inf}" stroke="gray" stroke-width="1"/>')
            # Línea eje Y
            texto_svg.append(f'<line x1="{margen_izq}" y1="{margen_sup}" x2="{margen_izq}" y2="{margen_inf}" stroke="gray" stroke-width="1"/>')
            
            # Escalas en eje X (5 marcas)
            num_marcas_x = 5
            for i in range(num_marcas_x + 1):
                frac = i / num_marcas_x
                x_pos = margen_izq + frac * (margen_der - margen_izq)
                valor = min_x + frac * (max_x - min_x)
                
                # Marca
                texto_svg.append(f'<line x1="{x_pos}" y1="{margen_inf}" x2="{x_pos}" y2="{margen_inf + 5}" stroke="gray" stroke-width="1"/>')
                # Texto
                texto_svg.append(f'<text x="{x_pos}" y="{margen_inf + 20}" font-size="10" text-anchor="middle" fill="black">{_fmt_num(valor)}</text>')
            
            # Escalas en eje Y (5 marcas)
            num_marcas_y = 5
            for i in range(num_marcas_y + 1):
                frac = i / num_marcas_y
                y_pos = margen_inf - frac * (margen_inf - margen_sup)
                valor = min_y + frac * (max_y - min_y)
                
                # Marca
                texto_svg.append(f'<line x1="{margen_izq - 5}" y1="{y_pos}" x2="{margen_izq}" y2="{y_pos}" stroke="gray" stroke-width="1"/>')
                # Texto
                texto_svg.append(f'<text x="{margen_izq - 10}" y="{y_pos + 4}" font-size="10" text-anchor="end" fill="black">{_fmt_num(valor)}</text>')
        
        content = "\n".join(self.elementos)
        textos = "\n".join(texto_svg)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">\n{bg}\n{content}\n{textos}\n</svg>'
        return svg

class Grafica:
    def __init__(self, titulo="", etiqueta_x="", etiqueta_y=""):
        self.titulo = titulo
        self.etiqueta_x = etiqueta_x
        self.etiqueta_y = etiqueta_y
        self.canvas = Canvas()
        self.datos = []
        # Estilos por defecto
        self.color_linea = (0, 0, 0)
        self.color_barras = (0, 0, 0)
        self.color_puntos = (0, 0, 0)
        self.grosor = 2
        self.tamano_punto = 4
        # ejes virtuales
        self.min_x = 0
        self.max_x = 1
        self.min_y = 0
        self.max_y = 1

    def establecer_datos(self, datos):
        self.datos = datos

    def configurar_ejes(self, min_x, max_x, min_y, max_y):
        if max_x == min_x:
            max_x = min_x + 1
        if max_y == min_y:
            max_y = min_y + 1
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def escalar_punto(self, x, y):
        pad = 0.1
        w = float(self.canvas.ancho)
        h = float(self.canvas.alto)
        dx = (self.max_x - self.min_x) if (self.max_x - self.min_x) != 0 else 1.0
        dy = (self.max_y - self.min_y) if (self.max_y - self.min_y) != 0 else 1.0
        px = pad * w + ((x - self.min_x) / dx) * (w * (1.0 - 2.0 * pad))
        py = (1.0 - pad) * h - ((y - self.min_y) / dy) * (h * (1.0 - 2.0 * pad))
        return Punto(px, py)


def crear_grafica_lineas(xs, ys, titulo="", ex="", ey=""):
    g = Grafica(titulo, ex, ey)
    datos = list(zip(xs, ys))
    g.establecer_datos(datos)
    
    min_x = min(xs) if xs else 0
    max_x = max(xs) if xs else 1
    min_y = min(ys) if ys else 0
    max_y = max(ys) if ys else 1
    g.configurar_ejes(min_x, max_x, min_y, max_y)

    pts = [g.escalar_punto(x, y) for x, y in datos]
    frags = []
    stroke = _rgb_to_str(g.color_linea)
    sw = max(1, int(g.grosor))
    
    for i in range(len(pts) - 1):
        p1 = pts[i]
        p2 = pts[i+1]
        frags.append(f'<line x1="{_fmt_num(p1.x)}" y1="{_fmt_num(p1.y)}" x2="{_fmt_num(p2.x)}" y2="{_fmt_num(p2.y)}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"/>')
    
    fill = _rgb_to_str(g.color_puntos)
    r = max(1, int(g.tamano_punto))
    for p in pts:
        frags.append(f'<circle cx="{_fmt_num(p.x)}" cy="{_fmt_num(p.y)}" r="{r}" fill="{fill}" />')

    for f in frags:
        g.canvas.agregar_elemento(f)
    return g

def crear_grafica_barras(categorias, valores, titulo="", ex="", ey=""):
    g = Grafica(titulo, ex, ey)
    datos = list(enumerate(valores))
    g.establecer_datos(datos)
    
    min_x = -0.5
    max_x = len(valores) - 0.5 if valores else 0.5
    min_y = 0
    max_y = max(valores) if valores else 1
    g.configurar_ejes(min_x, max_x, min_y, max_y)

    w = float(g.canvas.ancho)
    h = float(g.canvas.alto)
    total = len(valores)
    
    if total > 0:
        bar_width = (w * 0.7) / total
    else:
        bar_width = 10.0
    
    left0 = w * 0.15
    rects = []
    fill = _rgb_to_str(g.color_barras)
    
    for i, val in enumerate(valores):
        x = left0 + i * (bar_width + 4)
        denom = (max_y - min_y) if (max_y - min_y) != 0 else 1.0
        height_frac = (val - min_y) / denom
        rect_h = height_frac * (h * 0.6)
        y = h * 0.8 - rect_h
        rects.append(f'<rect x="{_fmt_num(x)}" y="{_fmt_num(y)}" width="{_fmt_num(bar_width)}" height="{_fmt_num(rect_h)}" fill="{fill}" />')

    for r in rects:
        g.canvas.agregar_elemento(r)
    return g

def crear_grafica_dispersion(xs, ys, titulo="", ex="", ey=""):
    g = Grafica(titulo, ex, ey)
    datos = list(zip(xs, ys))
    g.establecer_datos(datos)
    
    min_x = min(xs) if xs else 0
    max_x = max(xs) if xs else 1
    min_y = min(ys) if ys else 0
    max_y = max(ys) if ys else 1
    g.configurar_ejes(min_x, max_x, min_y, max_y)

    pts = [g.escalar_punto(x, y) for x, y in datos]
    fill = _rgb_to_str(g.color_puntos)
    r = max(1, int(g.tamano_punto))
    
    for p in pts:
        g.canvas.agregar_elemento(f'<circle cx="{_fmt_num(p.x)}" cy="{_fmt_num(p.y)}" r="{r}" fill="{fill}" />')
    return g

def crear_grafica_pastel(valores, etiquetas, titulo=""):
    g = Grafica(titulo, "", "")
    datos = list(zip(etiquetas, valores))
    g.establecer_datos(datos)
    return g

def guardar_grafica(grafica, ruta):
    svg = grafica.canvas.render_svg(
        grafica.titulo, 
        grafica.etiqueta_x, 
        grafica.etiqueta_y,
        grafica.min_x,
        grafica.max_x,
        grafica.min_y,
        grafica.max_y
    )
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(svg)


class _StanPlotInterpreter:
    """Intérprete de gráficas - instancia única compartida"""
    
    def __init__(self):
        self.current_graph = None

    def _min(self, lista):
        if not lista:
            return None
        m = lista[0]
        for x in lista:
            m = StanMath.min(m, x)
        return m

    def _max(self, lista):
        if not lista:
            return None
        m = lista[0]
        for x in lista:
            m = StanMath.max(m, x)
        return m

    def _sum(self, lista):
        s = 0
        for x in lista:
            s += x
        return s

    # CREACIÓN DE GRÁFICAS
    def crear_lineas(self, datos_x, datos_y, titulo="", eje_x="", eje_y=""):
        g = crear_grafica_lineas(datos_x, datos_y, titulo, eje_x, eje_y)
        if self.current_graph:
            g.color_linea = self.current_graph.color_linea
            g.color_puntos = self.current_graph.color_puntos
            g.grosor = self.current_graph.grosor
            g.tamano_punto = self.current_graph.tamano_punto
        self.current_graph = g
        return g

    def crear_barras(self, categorias, valores, titulo="", eje_x="", eje_y=""):
        g = crear_grafica_barras(categorias, valores, titulo, eje_x, eje_y)
        if self.current_graph:
            g.color_barras = self.current_graph.color_barras
        self.current_graph = g
        return g

    def crear_dispersion(self, datos_x, datos_y, titulo="", eje_x="", eje_y=""):
        g = crear_grafica_dispersion(datos_x, datos_y, titulo, eje_x, eje_y)
        if self.current_graph:
            g.color_puntos = self.current_graph.color_puntos
            g.tamano_punto = self.current_graph.tamano_punto
        self.current_graph = g
        return g

    def crear_pastel(self, valores, etiquetas, titulo=""):
        g = crear_grafica_pastel(valores, etiquetas, titulo)
        self.current_graph = g
        return g

    def crear_histograma(self, datos, num_bins, titulo="", eje_x="", eje_y=""):
        if not datos or num_bins <= 0:
            g = Grafica(titulo, eje_x, eje_y)
            g.establecer_datos([])
            self.current_graph = g
            return g

        min_val = self._min(datos)
        max_val = self._max(datos)
        ancho = (max_val - min_val) / num_bins if num_bins != 0 else 1.0
        bins = []
        
        for i in range(int(num_bins)):
            inicio = min_val + ancho * i
            fin = inicio + ancho
            count = 0
            for d in datos:
                if d >= inicio and d < fin:
                    count += 1
            bins.append((inicio, fin, count))

        categorias = [f"{_fmt_num(b[0])}-{_fmt_num(b[1])}" for b in bins]
        valores = [b[2] for b in bins]
        g = crear_grafica_barras(categorias, valores, titulo, eje_x, eje_y)
        self.current_graph = g
        return g

    def crear_area(self, datos_x, datos_y, titulo="", eje_x="", eje_y=""):
        g = crear_grafica_lineas(datos_x, datos_y, titulo, eje_x, eje_y)
        self.current_graph = g
        return g

    # ESTILOS
    def nuevo_canvas(self, ancho, alto):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.canvas = Canvas(ancho, alto)

    def color_fondo(self, r, g, b):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.canvas.color_fondo = (r, g, b)

    def titulo(self, texto):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.titulo = texto

    def color_barras(self, r, g, b):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.color_barras = (r, g, b)

    def color_puntos(self, r, g, b):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.color_puntos = (r, g, b)

    def color_linea(self, r, g, b):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.color_linea = (r, g, b)

    def tamano_puntos(self, tamano):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.tamano_punto = int(tamano)

    def grosor_linea(self, grosor):
        if not self.current_graph:
            self.current_graph = Grafica()
        self.current_graph.grosor = int(grosor)

    # GUARDAR
    def guardar(self, nombre_archivo):
        if not self.current_graph:
            raise Exception("No hay ninguna gráfica para guardar")
        guardar_grafica(self.current_graph, nombre_archivo)


StanPlot = _StanPlotInterpreter()


# Test directo de Python (no afecta a Deeper)
if __name__ == "__main__":
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 1, 8, 5]
    StanPlot.crear_lineas(x, y, "Test", "X", "Y")
    StanPlot.color_linea(200, 50, 50)
    StanPlot.color_puntos(20, 80, 200)
    StanPlot.guardar("test_grafica.svg")
    print("✓ Test completado: test_grafica.svg")

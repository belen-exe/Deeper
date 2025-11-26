from librerias.StanMath import StanMath

def __sum(lista):
    total = 0
    for v in lista:
        total += v
    return total

def __sum_producto(xs, ys):
    total = 0
    for i in range(len(xs)):
        total += xs[i] * ys[i]
    return total

def __sum_cuadrados(xs):
    total = 0
    for v in xs:
        total += v * v
    return total

# --------- Pendiente (m) ----------
def regresion_pendiente(xs, ys):
    n = len(xs)
    if n == 0:
        raise Exception("listas vacías en regresión")

    sx = __sum(xs)
    sy = __sum(ys)
    sxy = __sum_producto(xs, ys)
    sx2 = __sum_cuadrados(xs)

    num = n * sxy - sx * sy
    den = n * sx2 - sx * sx

    if den == 0:
        raise Exception("No se puede calcular pendiente, división por cero")

    return StanMath.div(num, den)

def regresion_intercepto(xs, ys):
    m = regresion_pendiente(xs, ys)
    n = len(xs)

    sx = __sum(xs)
    sy = __sum(ys)

    return StanMath.div(sy - m * sx, n)

def predecir(xs, m, b):
    res = []
    for x in xs:
        res.append(m * x + b)
    return res

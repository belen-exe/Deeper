from librerias.StanMath import StanMath

def _sum(xs):
    s = 0
    for x in xs:
        s += x
    return s

def _mean(xs):
    n = len(xs)
    return _sum(xs) / n if n else 0.0

def _dot(a, b):
    s = 0.0
    for i in range(len(a)):
        s += a[i] * b[i]
    return s

def _round2(x):
    try:
        return round(float(x), 2)
    except Exception:
        return x

def _round2_list(xs):
    return [_round2(x) for x in xs]

def _euclidean(a, b):
    s = 0.0
    for i in range(len(a)):
        d = a[i] - b[i]
        s += d * d
    return StanMath.raiz(s)

def _zeros(n):
    return [0.0] * n

def _copy_vec(v):
    return [float(x) for x in v]
    
# regresión lineal
def regresion_lineal(xs, ys, round2=True):
    n = len(xs)
    if n == 0 or len(ys) != n:
        raise Exception("Listas inválidas para regresión lineal")

    sx = _sum(xs)
    sy = _sum(ys)

    sxy = 0.0
    sx2 = 0.0
    for i in range(n):
        sxy += xs[i] * ys[i]
        sx2 += xs[i] * xs[i]

    num = n * sxy - sx * sy
    den = n * sx2 - sx * sx
    if den == 0:
        raise Exception("División por cero al calcular pendiente")

    m = num / den
    b = (sy - m * sx) / n

    if round2:
        return _round2(m), _round2(b)
    return m, b

def predecir_lineal(xs, m, b, round2=True):
    res = []
    for x in xs:
        v = m * x + b
        res.append(_round2(v) if round2 else v)
    return res

def regresion_pendiente(xs, ys):
    m, _ = regresion_lineal(xs, ys, round2=True)
    return m

def regresion_intercepto(xs, ys):
    _, b = regresion_lineal(xs, ys, round2=True)
    return b

def predecir(xs, m, b):
    return predecir_lineal(xs, m, b, round2=True)

# regresión logística
def _sigmoid(z):
    try:
        ez = StanMath.exp(-z)
        return 1.0 / (1.0 + ez)
    except Exception:
        try:
            ez = StanMath.exp(-z)
            return 1.0 / (1.0 + ez)
        except Exception:
            if z >= 0:
                return 1.0 / (1.0 + (StanMath.exp(-z)))
            return 1.0 / (1.0 + StanMath.exp(-z))

def _safe_log(x):
    if x <= 1e-15:
        x = 1e-15
    if x >= 1 - 1e-15:
        x = 1 - 1e-15
    return StanMath.log(x)

def regresion_logistica_train(X, y, lr=0.1, epochs=200):
    if not X or len(X) != len(y):
        raise Exception("Datos inválidos para regresión logística")
    n = len(X)
    d = len(X[0])

    w = _zeros(d)
    b = 0.0

    for ep in range(epochs):
        dw = _zeros(d)
        db = 0.0
        for i in range(n):
            xi = X[i]
            yi = y[i]
            z = _dot(w, xi) + b
            p = _sigmoid(z)
            err = p - yi
            for j in range(d):
                dw[j] += err * xi[j]
            db += err
        # actualizar (promedio gradiente)
        for j in range(d):
            w[j] -= lr * (dw[j] / n)
        b -= lr * (db / n)
    return w, b

def regresion_logistica_predict_proba(X, w, b):
    probs = []
    for xi in X:
        z = _dot(w, xi) + b
        probs.append(_sigmoid(z))
    return probs

def regresion_logistica_predict(X, w, b, threshold=0.5):
    probs = regresion_logistica_predict_proba(X, w, b)
    return [1 if p >= threshold else 0 for p in probs]

# perceptrón simple
def perceptron_train(X, y, epochs=100, lr=1.0):
    """
    Perceptrón binario. y in {0,1} -> internamente convertimos a {-1,1}
    Devuelve (w, b)
    """
    if not X or len(X) != len(y):
        raise Exception("Datos inválidos para perceptrón")
    n = len(X)
    d = len(X[0])
    w = _zeros(d)
    b = 0.0
    for _ in range(epochs):
        for i in range(n):
            xi = X[i]
            yi = 1 if y[i] == 1 else -1
            activation = _dot(w, xi) + b
            pred = 1 if activation >= 0 else -1
            if pred != yi:
                for j in range(d):
                    w[j] += lr * yi * xi[j]
                b += lr * yi
    return w, b

def perceptron_predict(X, w, b):
    res = []
    for xi in X:
        res.append(1 if (_dot(w, xi) + b) >= 0 else 0)
    return res

# ---------------- K-MEANS ----------------
def kmeans(X, k=2, max_iter=100):
    """
    K-means básico.
    Devuelve (centroids, labels)
    """
    if not X:
        return [], []
    n = len(X)
    d = len(X[0])
    # inicializar centroides tomando k muestras aleatorias
    k = min(k, n)
    # generar índices únicos
    inds = []
    while len(inds) < k:
        r = StanMath.randint(0, n-1)
        if r not in inds:
            inds.append(r)
    centroids = [_copy_vec(X[i]) for i in inds]
    labels = [0] * n

    for it in range(max_iter):
        changed = False
        # asignación
        for i in range(n):
            dists = [_euclidean(X[i], c) for c in centroids]
            min_idx = 0
            min_d = dists[0]
            for j in range(1, len(dists)):
                if dists[j] < min_d:
                    min_d = dists[j]; min_idx = j
            if labels[i] != min_idx:
                labels[i] = min_idx
                changed = True
        # recalcular centroides
        new_centroids = []
        for ci in range(len(centroids)):
            members = [X[i] for i in range(n) if labels[i] == ci]
            if not members:
                # re-inicializar como copia de un miembro aleatorio
                new_centroids.append(_copy_vec(centroids[ci]))
                continue
            mean_vec = []
            for dim in range(d):
                s = 0.0
                for m in members:
                    s += m[dim]
                mean_vec.append(s / len(members))
            new_centroids.append(mean_vec)
        # comprobar convergencia
        converged = True
        for a, b in zip(new_centroids, centroids):
            for i in range(len(a)):
                if abs(a[i] - b[i]) > 1e-9:
                    converged = False
                    break
            if not converged:
                break
        centroids = new_centroids
        if converged and not changed:
            break
    return centroids, labels

# K-NN
def knn_predict(X_train, y_train, x_query, k=3):
    if not X_train:
        raise Exception("KNN: no hay datos de entrenamiento")
    ds = []
    for xi, yi in zip(X_train, y_train):
        ds.append((_euclidean(xi, x_query), yi))
    ds.sort(key=lambda t: t[0])
    topk = ds[:k]
    votes = {}
    for _, lab in topk:
        votes[lab] = votes.get(lab, 0) + 1
    # seleccionar mayoritario
    best = None
    bestc = -1
    for lab, cnt in votes.items():
        if cnt > bestc:
            bestc = cnt
            best = lab
    return best

# regresión lineal compat:
def regresion_pendiente_wrapper(xs, ys):
    m, _ = regresion_lineal(xs, ys, round2=True)
    return m

def regresion_intercepto_wrapper(xs, ys):
    _, b = regresion_lineal(xs, ys, round2=True)
    return b

def predecir_wrapper(xs, m, b):
    return predecir_lineal(xs, m, b, round2=True)
    

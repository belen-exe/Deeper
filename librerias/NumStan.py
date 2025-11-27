from librerias.StanMath import StanMath

class NumStan:

    @staticmethod
    def shape(A):
        if not isinstance(A, list):
            raise ValueError("shape: el valor no es una matriz")

        if len(A) == 0:
            return (0, 0)

        if not isinstance(A[0], list):
            # es un vector
            return (1, len(A))

        return (len(A), len(A[0]))

    @staticmethod
    def es_matriz(A):
        return isinstance(A, list) and all(isinstance(fila, list) for fila in A)

    @staticmethod
    def es_vector(v):
        return isinstance(v, list) and all(not isinstance(x, list) for x in v)

    @staticmethod
    def mismo_shape(A, B):
        return NumStan.shape(A) == NumStan.shape(B)

    @staticmethod
    def es_cuadrada(A):
        filas, cols = NumStan.shape(A)
        return filas == cols

    @staticmethod
    def copiar(A):
        return [fila[:] for fila in A]


    # matrices
    @staticmethod
    def suma(A, B):
        if not NumStan.mismo_shape(A, B):
            raise ValueError("suma: las matrices no tienen el mismo tamaño")

        filas, cols = NumStan.shape(A)
        return [[A[i][j] + B[i][j] for j in range(cols)] for i in range(filas)]

    @staticmethod
    def resta(A, B):
        if not NumStan.mismo_shape(A, B):
            raise ValueError("resta: las matrices no tienen el mismo tamaño")

        filas, cols = NumStan.shape(A)
        return [[A[i][j] - B[i][j] for j in range(cols)] for i in range(filas)]

    @staticmethod
    def multiplicacion(A, B):
        filasA, colsA = NumStan.shape(A)
        filasB, colsB = NumStan.shape(B)

        if colsA != filasB:
            raise ValueError("multiplicacion: dimensiones incompatibles")

        R = [[0 for _ in range(colsB)] for _ in range(filasA)]

        for i in range(filasA):
            for j in range(colsB):
                for k in range(colsA):
                    R[i][j] += A[i][k] * B[k][j]

        return R

    @staticmethod
    def transpuesta(A):
        """Transpuesta de una matriz: filas ↔ columnas"""
        filas, cols = NumStan.shape(A)
        return [[A[i][j] for i in range(filas)] for j in range(cols)]

    @staticmethod
    def inversa(A):
        """Calcula la inversa de una matriz cuadrada usando Gauss-Jordan"""
        if not NumStan.es_cuadrada(A):
            raise ValueError("inversa: la matriz no es cuadrada")

        n = len(A)
        M = NumStan.copiar(A)

        # Matriz identidad
        I = [[1 if i == j else 0 for j in range(n)] for i in range(n)]

        # Gauss-Jordan
        for i in range(n):
            pivote = M[i][i]
            if pivote == 0:
                raise ValueError("inversa: pivote cero, matriz no invertible")

            # Normalizar fila
            for j in range(n):
                M[i][j] /= pivote
                I[i][j] /= pivote

            # Eliminar otras filas
            for k in range(n):
                if k != i:
                    factor = M[k][i]
                    for j in range(n):
                        M[k][j] -= factor * M[i][j]
                        I[k][j] -= factor * I[i][j]

        return I

    @staticmethod
    def hadamard(A, B):
        if not NumStan.mismo_shape(A, B):
            raise ValueError("hadamard: las matrices deben tener el mismo tamaño")

        filas, cols = NumStan.shape(A)
        return [[A[i][j] * B[i][j] for j in range(cols)] for i in range(filas)]

    @staticmethod
    def escalar(A, k):
        """Multiplica una matriz por un escalar: k × A"""
        filas, cols = NumStan.shape(A)
        return [[A[i][j] * k for j in range(cols)] for i in range(filas)]


    # vectores
    @staticmethod
    def dot(v1, v2):
        if len(v1) != len(v2):
            raise ValueError("dot: los vectores deben tener la misma longitud")
        return sum(v1[i] * v2[i] for i in range(len(v1)))

    @staticmethod
    def mat_vec(A, v):
        """Multiplicación matriz-vector: A × v"""
        filas, cols = NumStan.shape(A)

        if len(v) != cols:
            raise ValueError("mat_vec: dimensiones incompatibles")

        return [NumStan.dot(A[i], v) for i in range(filas)]


    # normalización
    @staticmethod
    def calcular_min_max(matriz):
        if len(matriz) == 0:
            raise ValueError("calcular_min_max: matriz vacía")
        
        n_cols = len(matriz[0])
        mins = []
        maxs = []
        
        for j in range(n_cols):
            columna = [matriz[i][j] for i in range(len(matriz))]
            mins.append(min(columna))
            maxs.append(max(columna))
        
        return {"mins": mins, "maxs": maxs}

    @staticmethod
    def normalizar_minmax(matriz):
        #Normaliza matriz usando Min-Max Scaling (0 a 1).

        params = NumStan.calcular_min_max(matriz)
        matriz_norm = NumStan.aplicar_normalizacion(matriz, params["mins"], params["maxs"])
        return {"matriz": matriz_norm, "params": params}

    @staticmethod
    def aplicar_normalizacion(matriz, mins, maxs):
        n_filas = len(matriz)
        n_cols = len(matriz[0])
        
        resultado = []
        for i in range(n_filas):
            fila_norm = []
            for j in range(n_cols):
                rango = maxs[j] - mins[j]
                if rango == 0:
                    # Evitar división por cero (columna constante)
                    fila_norm.append(0.0)
                else:
                    valor_norm = (matriz[i][j] - mins[j]) / rango
                    fila_norm.append(valor_norm)
            resultado.append(fila_norm)
        
        return resultado

    @staticmethod
    def desnormalizar(matriz_norm, mins, maxs):
        n_filas = len(matriz_norm)
        n_cols = len(matriz_norm[0])
        
        resultado = []
        for i in range(n_filas):
            fila_original = []
            for j in range(n_cols):
                valor_original = matriz_norm[i][j] * (maxs[j] - mins[j]) + mins[j]
                fila_original.append(valor_original)
            resultado.append(fila_original)
        
        return resultado

    # estandarización
    @staticmethod
    def calcular_media_std(matriz):
        if len(matriz) == 0:
            raise ValueError("calcular_media_std: matriz vacía")
        
        n_filas = len(matriz)
        n_cols = len(matriz[0])
        
        medias = []
        stds = []
        
        for j in range(n_cols):
            columna = [matriz[i][j] for i in range(n_filas)]
            
            # Calcular media
            media = sum(columna) / n_filas
            medias.append(media)
            
            # Calcular desviación estándar
            varianza = sum([(x - media) ** 2 for x in columna]) / n_filas
            std = varianza ** 0.5
            stds.append(std)
        
        return {"medias": medias, "stds": stds}

    @staticmethod
    def estandarizar(matriz):
        params = NumStan.calcular_media_std(matriz)
        matriz_std = NumStan.aplicar_estandarizacion(matriz, params["medias"], params["stds"])
        return {"matriz": matriz_std, "params": params}

    @staticmethod
    def aplicar_estandarizacion(matriz, medias, stds):
        #Aplica estandarización Z-score con parámetros dados.

        n_filas = len(matriz)
        n_cols = len(matriz[0])
        
        resultado = []
        for i in range(n_filas):
            fila_std = []
            for j in range(n_cols):
                if stds[j] == 0:
                    # Evitar división por cero (columna constante)
                    fila_std.append(0.0)
                else:
                    valor_std = (matriz[i][j] - medias[j]) / stds[j]
                    fila_std.append(valor_std)
            resultado.append(fila_std)
        
        return resultado

    # pesos
    @staticmethod
    def random_weights(filas, cols, rango=0.5):
        """Genera matriz de pesos aleatorios entre -rango y +rango."""
        return [[StanMath.random() * 2 * rango - rango for _ in range(cols)] for _ in range(filas)]

    @staticmethod
    def xavier_init(n_in, n_out):
        """
        Inicialización Xavier/Glorot.
        Rango: ±sqrt(6 / (n_in + n_out))
        
        Recomendado para: sigmoid y tanh
        """
        limite = (6.0 / (n_in + n_out)) ** 0.5
        return [[StanMath.random() * 2 * limite - limite for _ in range(n_out)] for _ in range(n_in)]

    @staticmethod
    def he_init(n_in, n_out):
        """
        Inicialización He.
        Rango: ±sqrt(6 / n_in)
        
        Recomendado para: ReLU
        """
        limite = (6.0 / n_in) ** 0.5
        return [[StanMath.random() * 2 * limite - limite for _ in range(n_out)] for _ in range(n_in)]

    @staticmethod
    def zeros(filas, cols):
        """Matriz de ceros - útil para inicializar biases"""
        return [[0.0 for _ in range(cols)] for _ in range(filas)]

    # métricas de regresión
    @staticmethod
    def mse(y_real, y_pred):
        if len(y_real) != len(y_pred):
            raise ValueError("mse: longitudes diferentes")
        
        n = len(y_real)
        return sum([(y_real[i] - y_pred[i]) ** 2 for i in range(n)]) / n

    @staticmethod
    def mae(y_real, y_pred):
        if len(y_real) != len(y_pred):
            raise ValueError("mae: longitudes diferentes")
        
        n = len(y_real)
        return sum([abs(y_real[i] - y_pred[i]) for i in range(n)]) / n

    @staticmethod
    def rmse(y_real, y_pred):
        return NumStan.mse(y_real, y_pred) ** 0.5

    @staticmethod
    def r2_score(y_real, y_pred):
        if len(y_real) != len(y_pred):
            raise ValueError("r2_score: longitudes diferentes")
        
        n = len(y_real)
        y_mean = sum(y_real) / n
        
        ss_tot = sum([(y_real[i] - y_mean) ** 2 for i in range(n)])
        ss_res = sum([(y_real[i] - y_pred[i]) ** 2 for i in range(n)])
        
        if ss_tot == 0:
            return 0.0
        
        return 1.0 - (ss_res / ss_tot)

    # metricas de clasificación
    @staticmethod
    def accuracy(y_real, y_pred):
        if len(y_real) != len(y_pred):
            raise ValueError("accuracy: longitudes diferentes")
        
        aciertos = sum([1 for i in range(len(y_real)) if y_real[i] == y_pred[i]])
        return aciertos / len(y_real)

    @staticmethod
    def confusion_matrix(y_real, y_pred):
        if len(y_real) != len(y_pred):
            raise ValueError("confusion_matrix: longitudes diferentes")
        
        tp = sum([1 for i in range(len(y_real)) if y_real[i] == 1 and y_pred[i] == 1])
        tn = sum([1 for i in range(len(y_real)) if y_real[i] == 0 and y_pred[i] == 0])
        fp = sum([1 for i in range(len(y_real)) if y_real[i] == 0 and y_pred[i] == 1])
        fn = sum([1 for i in range(len(y_real)) if y_real[i] == 1 and y_pred[i] == 0])
        
        return {"TP": tp, "TN": tn, "FP": fp, "FN": fn}

    @staticmethod
    def precision(y_real, y_pred):
        cm = NumStan.confusion_matrix(y_real, y_pred)
        if cm["TP"] + cm["FP"] == 0:
            return 0.0
        return cm["TP"] / (cm["TP"] + cm["FP"])

    @staticmethod
    def recall(y_real, y_pred):
        cm = NumStan.confusion_matrix(y_real, y_pred)
        if cm["TP"] + cm["FN"] == 0:
            return 0.0
        return cm["TP"] / (cm["TP"] + cm["FN"])

    @staticmethod
    def f1_score(y_real, y_pred):
        p = NumStan.precision(y_real, y_pred)
        r = NumStan.recall(y_real, y_pred)
        
        if p + r == 0:
            return 0.0
        
        return 2 * (p * r) / (p + r)

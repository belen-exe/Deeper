# NumStan.py
# Librería para operaciones de matrices en el lenguaje DEEPER.
# Sigue el mismo estilo de StanMath.

class NumStan:

    # =======================
    #   UTILIDADES INTERNAS
    # =======================

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

    # =======================
    #      OPERACIONES
    # =======================

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
        filas, cols = NumStan.shape(A)
        return [[A[i][j] for i in range(filas)] for j in range(cols)]

    # =======================
    #     MATRIZ INVERSA
    # =======================

    @staticmethod
    def inversa(A):
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

    # =======================
    #   PRODUCTO ELEMENTO A ELEMENTO
    # =======================

    @staticmethod
    def hadamard(A, B):
        if not NumStan.mismo_shape(A, B):
            raise ValueError("hadamard: las matrices deben tener el mismo tamaño")

        filas, cols = NumStan.shape(A)
        return [[A[i][j] * B[i][j] for j in range(cols)] for i in range(filas)]

    # =======================
    #   MULTIPLICAR POR ESCALAR
    # =======================

    @staticmethod
    def escalar(A, k):
        filas, cols = NumStan.shape(A)
        return [[A[i][j] * k for j in range(cols)] for i in range(filas)]

    # =======================
    #      VECTORES
    # =======================

    @staticmethod
    def dot(v1, v2):
        if len(v1) != len(v2):
            raise ValueError("dot: los vectores deben tener la misma longitud")
        return sum(v1[i] * v2[i] for i in range(len(v1)))

    @staticmethod
    def mat_vec(A, v):
        filas, cols = NumStan.shape(A)

        if len(v) != cols:
            raise ValueError("mat_vec: dimensiones incompatibles")

        return [NumStan.dot(A[i], v) for i in range(filas)]

    # =======================
    #   ACTIVACIONES PARA DL
    # =======================

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + (2.718281828459045 ** -x))

    @staticmethod
    def relu(x):
        return x if x > 0 else 0

    @staticmethod
    def softmax(v):
        m = max(v)
        exp = [(2.718281828459045 ** (x - m)) for x in v]
        s = sum(exp)
        return [e / s for e in exp]

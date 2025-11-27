class StanMath:
    # ---------- constantes ----------
    PI = 3.141592653589793
    E  = 2.718281828459045
    TAU = 2 * PI

    # ---------- RNG interno (LCG) ----------
    _rand_seed = 123456789  # valor por defecto

    @staticmethod
    def semilla(s):
        """Establece la semilla del generador."""
        StanMath._rand_seed = int(s) & 0xFFFFFFFF

    @staticmethod
    def random():
        # Parámetros clásicos del LCG
        a = 1664525
        c = 1013904223
        m = 2**32

        StanMath._rand_seed = (a * StanMath._rand_seed + c) % m
        return StanMath._rand_seed / m

    @staticmethod
    def randint(a, b):
        """Retorna un entero aleatorio entre a y b (incluidos)."""
        if a > b:
            raise ValueError("randint: a debe ser <= b")
        r = StanMath.random()
        return int(a + (b - a + 1) * r)

    # utilidades internas
    @staticmethod
    def _factorial_int(n: int) -> int:
        if n < 0:
            raise ValueError("factorial: n debe ser entero no negativo")
        r = 1
        for i in range(2, n + 1):
            r *= i
        return r

    @staticmethod
    def _abs(x):
        return x if x >= 0 else -x

    # módulo
    @staticmethod
    def mod(a, b):
        if b == 0:
            raise ValueError("mod: el divisor no puede ser cero")
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ValueError("mod: los valores deben ser numéricos")
        return a % b

    @staticmethod
    def _normalize_angle(x):
        k = int(x / StanMath.TAU)
        x -= k * StanMath.TAU
        if x > StanMath.PI:
            x -= StanMath.TAU
        if x < -StanMath.PI:
            x += StanMath.TAU
        return x

    # valor absoluto
    @staticmethod
    def abs(x):
        return StanMath._abs(x)

    # truncar
    @staticmethod
    def truncar(x):
        return int(x) if x >= 0 else -int(-x)

    # potencia
    @staticmethod
    def elevado(x, y):
        return x ** y

    # exponencial
    @staticmethod
    def exp(x, terms=60):
        result = 1.0
        numer = 1.0
        denom = 1.0
        for n in range(1, terms):
            numer *= x
            denom *= n
            result += numer / denom
        return result

    # log natural
    @staticmethod
    def log(x, iterations=40):
        if x <= 0:
            raise ValueError("log indefinido para x <= 0")

        y = 0.0
        if x > StanMath.E:
            k = 0
            xx = x
            while xx > StanMath.E:
                xx /= StanMath.E
                k += 1
            y = k + (xx - 1.0)
        else:
            y = x - 1.0

        for _ in range(iterations):
            ey = StanMath.exp(y)
            y -= (ey - x) / ey
        return y

    @staticmethod
    def log10(x):
        return StanMath.log(x) / StanMath.log(10.0)

    @staticmethod
    def log2(x):
        return StanMath.log(x) / StanMath.log(2.0)

    # trigonometría
    @staticmethod
    def sin(x, terms=30):
        x = StanMath._normalize_angle(x)
        result = 0.0
        num = x
        den = 1.0
        sign = 1
        for n in range(1, 2 * terms, 2):
            result += sign * num / den
            num *= x * x
            den *= (n + 1) * (n + 2)
            sign *= -1
        return result

    @staticmethod
    def cos(x, terms=30):
        x = StanMath._normalize_angle(x)
        result = 1.0
        num = 1.0
        den = 1.0
        sign = -1
        for n in range(2, 2 * terms, 2):
            num *= x * x
            den *= (n - 1) * n
            result += sign * num / den
            sign *= -1
        return result

    @staticmethod
    def tan(x):
        c = StanMath.cos(x)
        if StanMath._abs(c) < 1e-12:
            return float('inf') if StanMath.sin(x) >= 0 else float('-inf')
        return StanMath.sin(x) / c

    # trigonometría inversa
    @staticmethod
    def asin(x, iterations=40):
        if x < -1 or x > 1:
            raise ValueError("asin indefinido para |x|>1")

        y = x
        for _ in range(iterations):
            s = StanMath.sin(y)
            c = StanMath.cos(y)
            if StanMath._abs(c) < 1e-15:
                break
            y -= (s - x) / c
        return y

    @staticmethod
    def acos(x, iterations=40):
        return StanMath.PI/2 - StanMath.asin(x, iterations)

    @staticmethod
    def atan(x, iterations=40):
        y = x / (1 + StanMath._abs(x))
        for _ in range(iterations):
            s = StanMath.sin(y)
            c = StanMath.cos(y)
            denom = c * c
            if denom == 0:
                break
            y -= (s / c - x) * denom
        return y

    # conversión
    @staticmethod
    def grados(x):
        return x * 180.0 / StanMath.PI

    @staticmethod
    def radianes(x):
        return x * StanMath.PI / 180.0

    # raiz
    @staticmethod
    def raiz(x, iterations=50):
        if x < 0:
            raise ValueError("raiz: número negativo")
        if x == 0:
            return 0

        y = x if x < 1 else x / 2.0
        for _ in range(iterations):
            y = 0.5 * (y + x / y)
        return y

    # combinatoria
    @staticmethod
    def factorial(n):
        if not isinstance(n, int):
            if StanMath._abs(n - int(n)) < 1e-12:
                n = int(n)
            else:
                raise ValueError("factorial: n debe ser entero")
        return StanMath._factorial_int(n)

    @staticmethod
    def comb(n, r):
        if not (isinstance(n, int) and isinstance(r, int)):
            if (StanMath._abs(n - int(n)) < 1e-12 and 
                StanMath._abs(r - int(r)) < 1e-12):
                n = int(n); r = int(r)
            else:
                raise ValueError("comb: n y r deben ser enteros")

        if r < 0 or n < 0 or r > n:
            return 0

        return StanMath._factorial_int(n) // (
            StanMath._factorial_int(r) *
            StanMath._factorial_int(n - r)
        )

    @staticmethod
    def perm(n, r=None):
        if r is None:
            r = n

        if not (isinstance(n, int) and isinstance(r, int)):
            if (StanMath._abs(n - int(n)) < 1e-12 and
                StanMath._abs(r - int(r)) < 1e-12):
                n = int(n); r = int(r)
            else:
                raise ValueError("perm: n y r deben ser enteros")

        if r < 0 or n < 0 or r > n:
            return 0

        res = 1
        for i in range(n - r + 1, n + 1):
            res *= i
        return res

    # min / max
    @staticmethod
    def min(a, b):
        return a if a <= b else b

    @staticmethod
    def max(a, b):
        return a if a >= b else b

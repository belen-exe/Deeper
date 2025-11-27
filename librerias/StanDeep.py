# Librería para Redes Neuronales Multicapa (Perceptrón Multicapa)
# Usa StanMath internamente y está diseñada para ser simple y educativa
from librerias.StanMath import StanMath
from librerias.NumStan import NumStan


def custom_uniform(a, b):
    """Genera número aleatorio uniforme en [a, b) usando StanMath. random()"""
    return a + (b - a) * StanMath.random()

#     FUNCIONES DE ACTIVACIÓN
class ActivacionReLU:
    """ReLU: máximo entre 0 y x"""
    
    def forward(self, x):
        """Propagar hacia adelante"""
        return [max(0, v) for v in x]
    
    def backward(self, x, grad_output):
        """Propagar gradiente hacia atrás"""
        return [g if v > 0 else 0 for g, v in zip(grad_output, x)]


class ActivacionSigmoid:
    """Sigmoid: 1 / (1 + e^-x)"""
    
    def forward(self, x):
        """Propagar hacia adelante"""
        return [1 / (1 + StanMath.exp(-v)) for v in x]
    
    def backward(self, x, grad_output):
        """Propagar gradiente hacia atrás"""
        sig = self.forward(x)
        return [(s * (1 - s)) * g for s, g in zip(sig, grad_output)]


class ActivacionLineal:
    """Lineal: x (sin cambios)"""
    
    def forward(self, x):
        return x[:]
    
    def backward(self, x, grad_output):
        return grad_output[:]


#         CAPA DENSA

class CapaDensa:
    """Capa completamente conectada"""
    
    def __init__(self, n_entradas, n_salidas, activacion):
        """
        Inicializa la capa
        n_entradas: número de entradas
        n_salidas: número de neuronas
        activacion: objeto de activación (ActivacionReLU, ActivacionSigmoid, etc.)
        """
        # Inicialización Xavier (simple)
        limite = StanMath.raiz(1.0 / n_entradas)
        
        # Pesos: matriz de n_entradas x n_salidas
        self.W = [
            [custom_uniform(-limite, limite) for _ in range(n_salidas)]
            for _ in range(n_entradas)
        ]
        
        # Sesgos: vector de n_salidas
        self.b = [0.0] * n_salidas
        
        # Función de activación
        self.activacion = activacion
        
        # Cache para backpropagation
        self.x_cache = None
        self.z_cache = None
    
    def forward(self, x):
        """Propagar entrada hacia adelante"""
        self.x_cache = x[:]  # guardar para backprop
        
        # z = W^T * x + b
        z = []
        for j in range(len(self.b)):
            suma = self.b[j]
            for i in range(len(x)):
                suma += x[i] * self.W[i][j]
            z.append(suma)

        
        self.z_cache = z
        
        # Aplicar activación: a = activation(z)
        return self.activacion.forward(z)
    
    def backward(self, grad_output, lr):
        """
        Propagar gradiente hacia atrás y actualizar pesos
        grad_output: gradiente de la función de pérdida respecto a la salida
        lr: learning rate (tasa de aprendizaje)
        """
        # Gradiente respecto a z
        grad_z = self.activacion.backward(self.z_cache, grad_output)
        
        # Inicializar gradientes
        grad_W = [[0] * len(self.b) for _ in range(len(self.W))]
        grad_b = [0] * len(self.b)
        grad_x = [0] * len(self.x_cache)
        
        # Calcular gradientes
        for i in range(len(self.W)):
            for j in range(len(self.b)):
                grad_W[i][j] = self.x_cache[i] * grad_z[j]
        
        for j in range(len(self.b)):
            grad_b[j] = grad_z[j]
        
        for i in range(len(self. x_cache)):
            total = 0
            for j in range(len(self.b)):
                total += self.W[i][j] * grad_z[j]
            grad_x[i] = total
        
        # Actualizar pesos y sesgos (descenso por gradiente)
        for i in range(len(self.W)):
            for j in range(len(self.b)):
                self.W[i][j] -= lr * grad_W[i][j]
        
        for j in range(len(self.b)):
            self.b[j] -= lr * grad_b[j]
        
        return grad_x


#        FUNCIONES DE PÉRDIDA

class ErrorCuadratico:
    """Mean Squared Error (MSE) - para regresión"""
    
    def forward(self, y_real, y_pred):
        """Calcular pérdida"""
        return sum((p - r) ** 2 for p, r in zip(y_pred, y_real)) / len(y_real)
    
    def backward(self, y_real, y_pred):
        """Gradiente de la pérdida"""
        return [2 * (p - r) / len(y_real) for p, r in zip(y_pred, y_real)]


class Entropia:
    """Binary Cross Entropy - para clasificación binaria"""
    
    def forward(self, y_real, y_pred):
        """Calcular pérdida"""
        eps = 1e-15
        perdida = 0
        for r, p in zip(y_real, y_pred):
            p = max(eps, min(1 - eps, p))  # clip para evitar log(0)
            perdida -= r * StanMath.log(p) + (1 - r) * StanMath.log(1 - p)
        return perdida / len(y_real)
    
    def backward(self, y_real, y_pred):
        """Gradiente de la pérdida"""
        eps = 1e-15
        grad = []
        for r, p in zip(y_real, y_pred):
            p = max(eps, min(1 - eps, p))
            grad.append((p - r) / (p * (1 - p)) / len(y_real))
        return grad

#      OPTIMIZADOR BILL

class Bill:
    """
    Optimizador Bill (versión simplificada de Adam)
    Mantiene momentum para los pesos
    """
    
    def __init__(self, learning_rate=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8):
        """
        learning_rate: tasa de aprendizaje inicial
        beta1: decaimiento del primer momento (momentum)
        beta2: decaimiento del segundo momento (RMSprop)
        epsilon: pequeño valor para evitar división por cero
        """
        self.lr = learning_rate
        self. beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        
        # Momentos (se inicializan al primer uso)
        self.m = None  # primer momento (momentum)
        self.v = None  # segundo momento (RMSprop)
        self.t = 0    # contador de pasos
    
    def inicializar(self, parametros):
        """Inicializar momentos con la forma de los parámetros"""
        self. m = []
        self.v = []
        
        # Para cada parámetro (peso o sesgo), crear su momento correspondiente
        for param in parametros:
            self.m.append([[0.0] * len(param[i]) if isinstance(param[i], list) else 0.0 
                          for i in range(len(param))])
            self.v.append([[0.0] * len(param[i]) if isinstance(param[i], list) else 0.0 
                          for i in range(len(param))])
    
    def actualizar(self, parametros, gradientes):
        """
        Actualizar parámetros usando Bill
        parametros: lista de pesos/sesgos
        gradientes: lista de gradientes correspondientes
        """
        if self.m is None:
            self.inicializar(parametros)
        
        self.t += 1
        params_actualizados = []
        
        for param_idx, (param, grad) in enumerate(zip(parametros, gradientes)):
            if isinstance(param, list) and isinstance(param[0], list):
                # Es una matriz (pesos)
                param_nuevo = []
                for i in range(len(param)):
                    fila = []
                    for j in range(len(param[i])):
                        g = grad[i][j] if isinstance(grad[i], list) else grad[i]
                        
                        # Actualizar momentos
                        self.m[param_idx][i][j] = (self.beta1 * self.m[param_idx][i][j] + 
                                                    (1 - self.beta1) * g)
                        self.v[param_idx][i][j] = (self.beta2 * self.v[param_idx][i][j] + 
                                                    (1 - self.beta2) * (g * g))
                        
                        # Corrección de sesgo
                        m_hat = self.m[param_idx][i][j] / (1 - self.beta1 ** self.t)
                        v_hat = self.v[param_idx][i][j] / (1 - self.beta2 ** self.t)
                        
                        # Actualizar parámetro
                        nuevo_valor = param[i][j] - self.lr * m_hat / (StanMath.raiz(v_hat) + self.epsilon)
                        fila.append(nuevo_valor)
                    param_nuevo.append(fila)
                params_actualizados.append(param_nuevo)
            else:
                # Es un vector (sesgos)
                param_nuevo = []
                for i in range(len(param)):
                    g = grad[i]
                    
                    # Actualizar momentos
                    self.m[param_idx][i] = self.beta1 * self.m[param_idx][i] + (1 - self.beta1) * g
                    self. v[param_idx][i] = self.beta2 * self.v[param_idx][i] + (1 - self. beta2) * (g * g)
                    
                    # Corrección de sesgo
                    m_hat = self.m[param_idx][i] / (1 - self.beta1 ** self.t)
                    v_hat = self.v[param_idx][i] / (1 - self.beta2 ** self.t)
                    
                    # Actualizar parámetro
                    nuevo_valor = param[i] - self.lr * m_hat / (StanMath.raiz(v_hat) + self.epsilon)
                    param_nuevo.append(nuevo_valor)
                params_actualizados.append(param_nuevo)
        
        return params_actualizados


#      RED NEURONAL MULTICAPA

class PerceptronMulticapa:
    """Red Neuronal Multicapa (MLP)"""
    
    def __init__(self):
        """Inicializar la red vacía"""
        self.capas = []
        self.funcion_perdida = None
        self.optimizador = None
    
    def agregar_capa(self, n_entradas, n_salidas, activacion="relu"):
        """
        Agregar una capa a la red
        n_entradas: número de entradas a esta capa
        n_salidas: número de neuronas de esta capa
        activacion: "relu", "sigmoid" o "lineal"
        """
        # Seleccionar función de activación
        if activacion == "sigmoid":
            act = ActivacionSigmoid()
        elif activacion == "lineal":
            act = ActivacionLineal()
        else:  # por defecto relu
            act = ActivacionReLU()
        
        # Crear capa y agregarla
        capa = CapaDensa(n_entradas, n_salidas, act)
        self.capas.append(capa)
    
    def compilar(self, funcion_perdida="mse", learning_rate=0.01):
        """
        Compilar la red (preparar para entrenamiento)
        funcion_perdida: "mse" (regresión) o "entropia" (clasificación)
        learning_rate: tasa de aprendizaje
        """
        if funcion_perdida == "entropia":
            self.funcion_perdida = Entropia()
        else:  # por defecto mse
            self. funcion_perdida = ErrorCuadratico()
        
        # Crear optimizador Bill
        self.optimizador = Bill(learning_rate=learning_rate)
    
    def forward(self, x):
        """Propagar entrada hacia adelante a través de toda la red"""
        salida = x
        for capa in self. capas:
            salida = capa.forward(salida)
        return salida
    
    def backward(self):
        """Propagar gradientes hacia atrás (sin actualizar pesos aún)"""
        # Este método es auxiliar, la actualización se hace en entrenar()
        pass
    
    def entrenar(self, X, y, epochs=10, lr=0.01, verbose=True):
        """
        Entrenar la red
        X: lista de ejemplos (cada ejemplo es una lista de entradas)
        y: lista de etiquetas (cada etiqueta es una lista de valores reales)
        epochs: número de épocas
        lr: tasa de aprendizaje
        verbose: mostrar pérdida durante el entrenamiento
        """
        if not self.funcion_perdida:
            raise Exception("Error: debes compilar la red primero con . compilar()")
        
        if len(X) != len(y):
            raise Exception("Error: X e y deben tener la misma longitud")
        
        # Entrenar por épocas
        for epoch in range(epochs):
            perdida_total = 0
            
            # Pasar cada ejemplo
            for x_ejemplo, y_ejemplo in zip(X, y):
                # Forward pass
                y_pred = self.forward(x_ejemplo)
                
                # Calcular pérdida
                perdida = self.funcion_perdida.forward(y_ejemplo, y_pred)
                perdida_total += perdida
                
                # Backward pass
                grad = self.funcion_perdida. backward(y_ejemplo, y_pred)
                
                # Propagar gradiente hacia atrás a través de todas las capas
                for capa in reversed(self.capas):
                    grad = capa.backward(grad, lr)
            
            # Mostrar progreso
            if verbose and (epoch + 1) % max(1, epochs // 10) == 0:
                perdida_promedio = perdida_total / len(X)
                mostrar(f"Época {epoch + 1}/{epochs}, Pérdida: {perdida_promedio}")
    
    def predecir(self, X):
        """
        Hacer predicciones con la red entrenada
        X: lista de ejemplos
        Retorna: lista de predicciones
        """
        return [self.forward(x) for x in X]
    
    def evaluar(self, X, y):
        """
        Evaluar la red en datos de prueba
        X: ejemplos
        y: etiquetas reales
        Retorna: pérdida promedio
        """
        if not self.funcion_perdida:
            raise Exception("Error: debes compilar la red primero")
        
        perdida_total = 0
        for x_ejemplo, y_ejemplo in zip(X, y):
            y_pred = self.forward(x_ejemplo)
            perdida = self.funcion_perdida.forward(y_ejemplo, y_pred)
            perdida_total += perdida
        
        return perdida_total / len(X)


#     FUNCIONES DE UTILIDAD

def mostrar(msg):
    """Mostrar mensaje (compatible con Deeper)"""
    print(msg)


# Crear una instancia global para uso en Deeper
MLP = PerceptronMulticapa()

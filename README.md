# Deeper - Lenguaje de programación

Deeper es un lenguaje de programación pensado como un DSL (Lenguaje para un dominio específico) enfocado para correr desde operaciones aritméticas básicas, funciones, condicionales, bucles, expresiones, importación de librerias, carga de archivos, etc; hasta su objetico principal: Deep Learning. Diseñado con ANTLR4 + Python y pensado en su visualización como PSeInt sin quitar la sencillez de Python.

>[!IMPORTANT]
> ***Elaborado por:** Laura Sophia Hernández, Angie Lorena López y María Belén Peña*

## Gramática

Para entender un poco mejor la sintáxis del lenguaje de programación.

### Palabras reservadas y Tipos

- IF       : 'si';
- ELSE     : 'sino';
- WHILE    : 'mientras';
- FOR      : 'por';
- IN       : 'en';
- DEF      : 'fun';
- RETURN   : 'retornar';
- FIN      : 'fin';
- INT      : 'entero';
- FLOAT    : 'decimal';
- BOOLEANO : 'bool';
- BOOLEANO : 'verdadero' | 'falso';
- STRING   : 'cadena';
- LIST     : 'lista';
- DICC     : 'diccionario';
- MATRIZ   : 'matriz';
- IMPORT   : 'importar';
- AS       : 'como';

### Para funciones, declaraciones y condicionales

Al igual que en lenguajes como C, C++, Java, JavaScript, Kotlin, C#, Go, PHP, Rust, etc. Se conservó el uso del **;**, para funciones y condicionales se habre el bloque con **:** y cierra con **fin** para una estructura más organizada y reconocible a la gramática. 

---

## Componentes y estructura principal de Deeper

| Componente / carpeta                                             | Qué contiene / para qué sirve                                                                                                                                                                                                                                                                     |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`generacion/DeeperLexer.g4` + `DeeperParser.g4`**              | Gramática del lenguaje: define la sintaxis — tipos, palabras reservadas, expresiones, listas, funciones, bucles, etc. ([GitHub][1])                                                                                                                                                               |
| **`visitor/ejecutar.py`**                                        | “Intérprete” del AST parseado: recorre el árbol generado por ANTLR para ejecutar el programa escrito en Deeper. Es el núcleo que da vida al lenguaje. ([GitHub][1])                                                                                                                               |
| **`runtime/mostrar.py`**                                         | Etiqueta “built-in”: funciones básicas disponibles sin importar librería (como `mostrar`, operaciones matemáticas de base, conversión, etc.). Usa internamente una librería “tranquila” de math (que llamaban `StanMath`). ([GitHub][1])                                                          |
| **`ejemplos/`**                                                  | Archivos de ejemplo escritos en la sintaxis Deeper (`*.dp`), para demostrar uso de librerías, gráficos, regresión, etc. ([GitHub][1])                                                                                                                                                             |
| **`main.py` / `repl.py`**                                        | Punto de entrada del intérprete: recibe un archivo `.dp`, lo parsea, ejecuta con el visitor; también puede ofrecer un REPL interactivo. ([GitHub][1])                                                                                                                                             |
---

## Estructura de las librerías en Deeper

Cada archivo dentro de librerias/ actúa como un módulo Python que el intérprete puede importar desde Deeper, usando:

```
importar NombreLibreria como alias;
```

Por eso, cada biblioteca expone funciones o clases de Python que luego pueden ser llamadas desde Deeper.

### StanMath.py → Biblioteca matemática nativa

#### Función: proveer cálculo matemático básico y avanzado sin depender de NumPy, 100% en Python.

##### Contenido típico:

- Aritmética:	abs, potencia, mod
- Trigonometría:	sen, cos, tan, atan, etc.
- Logaritmos y exponenciales:	log, exp, ln
- Combinatoria:	factorial, nCr, nPr
- Miscelánea:	raiz, redondear, aleatorio

#### Estructura real del archivo:

librerias/StanMath.py

```
  import math
  
  class StanMath:
      PI = math.pi
      E  = math.e
  
      def sen(x): ...
      def cos(x): ...
      def log(x): ...
      def factorial(n): ...
      # etc.
```

#### Qué obtiene el usuario en Deeper:

```
importar StanMath como m;

mostrar(m.PI);
mostrar(m.sen(3.14));
```
---

### StanPlot.py → Biblioteca de gráficos en SVG

#### Función: generar gráficas SVG (barras, líneas, dispersión, regresión) desde Deeper.

#### Contenido:

- Clase Canvas:	Contiene la imagen y elementos SVG
- Clase Grafica:	Configura ejes, estilos, datos
- Creadores:	crear_lineas(), crear_barras(), crear_dispersion(), crear_regresion()
- Estilos:	color_linea(), color_puntos(), color_fondo(), grosor_linea()...
- Guardado:	guardar() produce un .svg

#### Estructura principal:

```
StanPlot.py
├── utilidades (_rgb_to_str, _fmt_num)
├── class Punto
├── class Canvas
│   ├── agregar_elemento()
│   ├── render_svg()
├── class Grafica
│   ├── escalar_punto()
│   ├── configurar_ejes()
├── creadores de gráfica
│   ├── crear_grafica_lineas()
│   ├── crear_grafica_barras()
│   ├── crear_grafica_dispersion()
│   ├── crear_regresion()
├── guardar_grafica()
└── class _StanPlotInterpreter (API expuesta)
```

#### Usado desde Deeper:

```
importar StanPlot como p;

p.crear_barras(["A","B","C"], [3,5,2], "Ejemplo", "x","y");
p.color_barras(0,120,200);
p.guardar("salida.svg");
```

---

### StanLearn.py → Biblioteca de aprendizaje automático

#### Función: proveer ML básico sin dependencias externas.

#### Contiene:

- Regresión lineal:	regresion_pendiente, regresion_intercepto, predecir
- Regresión logística:	logistica_fit, logistica_pred
- Perceptrón simple:	entrenar_perceptron, predecir_perceptron
- KNN:	knn_clasificar
- K-means:	kmeans_cluster

#### Estructura base:

```
StanLearn.py
├── utilidades (distancias, productos escalares)
├── regresión lineal
│   ├── regresion_pendiente()
│   ├── regresion_intercepto()
│   ├── predecir()
├── regresión logística (según versión)
├── perceptrón simple
└── clustering (KNN, kmeans)
```

#### Invocado desde Deeper así:

```
importar StanLearn como sl;

lista x = [1,2,3];
lista y = [2,4,6];

decimal m = sl.regresion_pendiente(x,y);
mostrar(m);
```

---

### NumStan.py → Álgebra y estadística numérica

#### Objeto principal: NumStan (toda la librería es estática)

#### ¿Qué hace?

- Calcula álgebra matricial (suma, producto, inversa…)
- Maneja vectores (dot, mat_vec)
- Normaliza/estandariza datos
- Inicializa pesos para redes neuronales
- Métricas de regresión y clasificación

#### Estructura conceptual

- Identificación de tipos:	shape, es_matriz, es_vector, mismo_shape, es_cuadrada, copiar
- Operaciones matriciales:	suma, resta, multiplicacion, hadamard, escalar, transpuesta, inversa
- Operaciones vectoriales:	dot, mat_vec
- Normalización Min-Max:	calcular_min_max, normalizar_minmax, aplicar_normalizacion, desnormalizar
- Estandarización: Z-score	calcular_media_std, estandarizar, aplicar_estandarizacion
- Inicialización de pesos:	random_weights, xavier_init, he_init, zeros
- Métricas regresión:	mse, mae, rmse, r2_score
- Métricas clasificación:	accuracy, precision, recall, f1_score, confusion_matrix

#### Uso típico en Deeper: cuando el usuario construye redes, normaliza datos o trabaja con matrices.

---

### StanDeep.py → Redes Neuronales Multicapa (MLP)

#### Objetos principales:

- PerceptronMulticapa (red completa)
- CapaDensa (capa fully-connected)
- Activaciones: ReLU, Sigmoid, Lineal
- Pérdidas: ErrorCuadratico, Entropia
- Optimizador: Bill (similar a Adam)

#### ¿Qué hace?

Permite entrenar y usar una red neuronal con forward, backward y optimización.

#### Estructura conceptual

- Activaciones:	ActivacionReLU, ActivacionSigmoid, ActivacionLineal
- Capa:	CapaDensa (pesos, biases, forward, backward)
- Pérdidas:	ErrorCuadratico (regresión), Entropia (clasificación)
- Optimizador	Bill: momentum + RMS como Adam
- Red	PerceptronMulticapa: agregar capas, compilar, entrenar, predecir, evaluar
- Utilidad	mostrar() y una instancia global MLP

---

### archivos.py → I/O para archivos

#### ¿Qué hace?

Permite leer y escribir archivos en Stan/Deeper con manejo de errores.

#### Funciones:

- leer_archivo(ruta):	Devuelve el texto del archivo
- escribir_archivo(nombre, contenido):	Escribe un archivo y devuelve True/False

Todos los errores se transforman en DeeperError, no Python exceptions.

---

### patos.py 🦆 → Mini-DataFrame tipo pandas 

#### Objetivo: manipular datos tabulares (filtrar, seleccionar, exportar…)

#### Estructura conceptual

- Info:	columnas, detectar_tipos
- Selección:	seleccionar, filtrar
- Edición:	reemplazar, llenar_na
- Exportación:	guardar_csv
- Conversión a datos numéricos:	to_matriz, to_etiqueta
- Dataset: split	div_entreno

Además: leer_csv(ruta) convierte CSV → PatosFrame.

---

## ¿Qué representa Deeper?

Deeper es un experimento educativo: un lenguaje simple, diseñado para que estudiantes o entusiastas de ML/estadística/algoritmos puedan:

- escribir pseudocódigo estructurado,
- hacer cálculos matemáticos sin depender de bibliotecas externas,
- extender con librerías "internas" (plots, ML),
- aprender los mecanismos internos de un intérprete / compilador / runtime,
- combinar programación, álgebra, ML, visualización — todo en un solo entorno controlado.

# Deeper - Lenguaje de programación

Deeper es un lenguaje de programación pensado como un DSL (Lenguaje para un dominio específico) enfocado para correr desde operaciones aritméticas básicas, funciones, condicionales, bucles, expresiones, importación de librerias, carga de archivos, etc; hasta su objetico principal: Deep Learning. Diseñado con ANTLR4 + Python y pensado en su visualización como PSeInt sin quitar la sencillez de Python.

>[!IMPORTANT]
> ***Elaborado por:** Laura Sophia Hernández, Angie Lorena López y María Belén Peña*


## 📝 Gramática

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

Al igual que en lenguajes como C, C++, Java, JavaScript, Kotlin, C#, Go, PHP, Rust, etc. Se conservó el uso del **;** y para funciones y condicionales se habre el bloque con **:** y cierra con **fin** para una estructura más organizada y reconocible a la gramática. 


## 📚 Librerías

### StanMath

Librería de math implementada en Deeper como 'StanMath' con o sin alias es posible.

- truncar(x)
- exp(x) → e^x 
- log(x) → log natural 
- log10(x) → log base 10 
- log2(x) → log base 2 
- pow(x, y) → potencia 
- trigonometria (sin, cos, tan, asin, acos, atan)
- conversion de ángulos (radinaes, grados)
- funciones combinatorias (factorial, combinación, permutación)
- constantes (pi, e, tau)

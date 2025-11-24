parser grammar DeeperParser;

options { tokenVocab = DeeperLexer; }

// programa
programa
    : (instruccion)* EOF
    ;

// INSTRUCCIÓN

instruccion
    : declaracion_variable SEMI
    | asignacion SEMI
    | llamada_funcion SEMI
    | retornar
    | condicion
    | bucle_mientras
    | importar_stmt SEMI
    | bucle_por
    | definicion_funcion
    ;

retornar
    : RETORNAR expr SEMI
    ;

// declaración
declaracion_variable
    : tipo ID (ASSIGN expr)?
    ;

asignacion
    : ID ASSIGN expr
    ;

// tipos
tipo
    : ENTERO
    | DECIMAL
    | BOOL_T
    | CADENA_T
    | LISTA_T
    | DICC_T
    | MATRIZ_T
    ;

// FUNCIONES

definicion_funcion
    : FUN ID LPAREN parametros? RPAREN COLON
      (instruccion)*
      FIN
    ;

parametros
    : ID (COMMA ID)*
    ;

llamada_funcion
    : ID LPAREN argumentos? RPAREN
    ;

argumentos
    : expr (COMMA expr)*
    ;

// condicionales
condicion
    : SI expr COLON
      (instruccion)*
      ( SINO COLON
        (instruccion)*
      )?
      FIN
    ;

// bucles
bucle_mientras
    : MIENTRAS expr COLON
      (instruccion)*
      FIN
    ;

bucle_por
    : POR ID EN expr COLON
      (instruccion)*
      FIN
    ;

// expresiones
expr
    : orExpr
    ;

orExpr
    : andExpr ( OR andExpr )*
    ;

andExpr
    : eqExpr ( AND eqExpr )*
    ;

eqExpr
    : relExpr ((EQ|NEQ) relExpr)*
    ;

relExpr
    : addExpr ((LT|GT|LE|GE) addExpr)*
    ;

addExpr
    : mulExpr ((PLUS|MINUS) mulExpr)*
    ;

mulExpr
    : unaryExpr ((MUL|DIV|MOD) unaryExpr)*
    ;

unaryExpr
    : NOT unaryExpr
    | MINUS unaryExpr
    | atom
    ;

atom
    : primary atomSuffix*
    ;

// obj.x
atomSuffix
    : DOT ID
    | DOT llamada_funcion
    | LBRACK expr RBRACK
    ;
    
primary
    : NUMBER
    | STRING
    | BOOL_LIT
    | llamada_funcion
    | ID
    | LPAREN expr RPAREN
    | lista
    | diccionario
    | matriz
    ;

// estructura de datos
lista
    : LBRACK (expr (COMMA expr)*)? RBRACK
    ;

diccionario
    : LBRACE (clave_valor (COMMA clave_valor)*)? RBRACE
    ;

clave_valor
    : STRING COLON expr
    ;
    
importar_stmt
    : IMPORTAR ID (COMO ID)?
    ;

matriz
    : LBRACK (lista (COMMA lista)*)? RBRACK
    ;

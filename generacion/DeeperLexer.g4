lexer grammar DeeperLexer;

// PALABRAS RESERVADAS
SI       : 'si';
SINO     : 'sino';
MIENTRAS : 'mientras';
POR      : 'por';
EN       : 'en';
FUN      : 'fun';
RETORNAR : 'retornar';
FIN      : 'fin';
IMPORTAR : 'importar';
COMO     : 'como';

// TIPOS
ENTERO     : 'entero';
DECIMAL    : 'decimal';
BOOL_T     : 'bool';
CADENA_T   : 'cadena';
LISTA_T    : 'lista';
DICC_T     : 'diccionario';
MATRIZ_T   : 'matriz';
DATAFRAME_T: 'dataframe';

// LITERALES
BOOL_LIT : 'verdadero' | 'falso';
NUMBER   : [0-9]+ ('.' [0-9]+)?;
STRING   : '"' (~["\r\n])* '"' ;

// IDENTIFICADORES
ID : [a-zA-Z_][a-zA-Z0-9_]* ;

// OPERADORES
PLUS  : '+' ;
MINUS : '-' ;
MUL   : '*' ;
DIV   : '/' ;
MOD   : '%' ;
POW   : '^' ;
ASSIGN : '=' ;

COLON  : ':' ;
COMMA  : ',' ;
SEMI   : ';' ;
DOT    : '.' ;

LPAREN : '(' ;
RPAREN : ')' ;
LBRACK : '[' ;
RBRACK : ']' ;
LBRACE : '{' ;
RBRACE : '}' ;

EQ  : '==' ;
NEQ : '!=' ;
LE  : '<=' ;
GE  : '>=' ;
LT  : '<' ;
GT  : '>' ;

OR  : '||' ;
AND : '&&' ;
NOT : '!' ;

// Comentarios tipo //
COMMENT : '//' ~[\r\n]* -> skip ;

WS : [ \t\r\n]+ -> skip ;

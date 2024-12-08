grammar SQL;

options { 
  caseInsensitive = true;
}

// parser rules
sql_statement: (select_statement | delete_statement | insert_statement) (SEMICOLON (select_statement | delete_statement | insert_statement)+)* SEMICOLON EOF;

select_statement: SELECT column_list (FROM (table_list | OPENPAR select_statement CLOSEPAR)+ where_clause?)?;
delete_statement: DELETE FROM table_list where_clause?;
insert_statement: INSERT INTO table_list insert_column_list? VALUES values_list;

table_list: WORD+ (',' WORD+)*;
column_list: '*' | column (',' column)*;
values_list: OPENPAR value (',' value)* CLOSEPAR;
insert_column_list: '('column (',' column)*')';

where_clause: WHERE condition_list;
condition_list: expression | expression+ ((AND | OR) expression)+;

expression: column operator value;

column: (WORD | STRING | TCNAME | NUMBER) (',' (WORD | STRING | TCNAME | NUMBER))*;
value: STRING | NUMBER | NULL;

operator: '=' | '<>' | '<' | '>' | '<=' | '>=';

TCNAME: WORD (DOT WORD)+;

// lexer rules
SELECT: 'select';
FROM: 'from';
WHERE: 'where';
AND: 'and';
OR: 'or';
SEMICOLON: ';';
DELETE: 'delete';
INSERT: 'insert';
INTO: 'into';
VALUES: 'values';
NULL: 'null';
DOT: '.';
OPENPAR: '(';
CLOSEPAR: ')';
WORD: [a-zA-Z_][a-zA-Z_0-9]*;

NUMBER: [0-9]+;
STRING: '\'' .*? '\'';

WS: [ \t\n\r]+ -> skip;

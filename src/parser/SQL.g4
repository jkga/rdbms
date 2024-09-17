grammar SQL;

options { 
  caseInsensitive = true;
}

// parser rules
sql_statement: (select_statement | delete_statement | insert_statement) (SEMICOLON (select_statement | delete_statement | insert_statement)+)* SEMICOLON EOF;

select_statement: SELECT column_list (FROM (table | OPENPAR select_statement CLOSEPAR)+ where_clause?)?;
delete_statement: DELETE FROM table where_clause?;
insert_statement: INSERT INTO table insert_column_list? VALUES values_list;

column_list: '*' | column (',' column)*;
values_list: '('value (',' value)*')';
insert_column_list: '('column (',' column)*')';

where_clause: WHERE condition;
condition: expression | expression+ ((AND | OR) expression)+;

expression: column operator value;

column: (WORD | TCNAME) (',' (WORD | TCNAME))*;
table: WORD+ (',' WORD+)*;
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
WORD: [a-z_]+[0-9]*;

NUMBER: [0-9]+;
STRING: '\'' .*? '\'';

WS: [ \t\n\r]+ -> skip;

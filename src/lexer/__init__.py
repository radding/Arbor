import ply.lex as lex

class LexerError(Exception): pass

reserved = {
   'if' : 'IF',
   'else' : 'ELSE',
   'done' : "DONE",
   'return': "RETURN",
   "const" : "CONST",
   "let": "LET",
   'int': 'INTTYPE',
   'float': 'FLOATTYPE',
   'char': 'CHARTYPE',
   'function': 'FUNCTIONTYPE',
}

tokens = [
    "INT",
    "FLOAT",
    "PLUS",
    "MULTI",
    "DIV",
    "SUB",
    "NAME",
    "LPAREN",
    "RPAREN",
    "COLON",
    "COMMA",
    "SEMICOLON",
    "ARROW",
    "EQ",
    "OCT",
    "HEX",
    'GT',
    'LT',
    'GTE',
    'LTE',
    'CHAR',
    "STRING",
    'EQCOMP',
    'NEQ',
    'AND',
    'OR',
    'NOT'
] + list(reserved.values())

t_INT = r'-?[1-9]+[0-9]*'
t_FLOAT = r'-?[0-9]*\.[0-9]+'
t_PLUS = r'\+'
t_MULTI = r'\*'
t_DIV = r'\/'
t_SUB = r'-'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COLON = r'\:'
t_COMMA = r'\,'
t_SEMICOLON = r'\;'
t_ARROW = r'\-\>'
t_EQ = r'='
t_EQCOMP = r'=='
t_NEQ = r'\!='
t_LT = r'<'
t_GT = r'>'
t_LTE = r'<='
t_GTE = r'>='
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'\!'

t_ignore = ' \t'

def t_HEX(t):
    r'\b0x[0-9a-fA-F]+\b'
    t.value = str(int(t.value, 16))
    return t

def t_OCT(t):
    r'\b0[0-9]+\b'
    t.value = str(int(t.value, 8))
    return t

def t_CHAR(t):
     r'\'.\''
     t.value = t.value[1]
     return t

def t_STRING(t):
     r'".*"'
     t.value = t.value[1:-1]
     return t

def t_NAME(t):
    r'\b[a-zA-Z_]+([a-zA-Z0-9_])*\b'
    t.type = reserved.get(t.value, "NAME")
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_BLOCKCOMMNET(t):
    r'/\*(.|\n)*\*/'
    pass

def t_COMMENT(t):
    r'//.*'
    pass

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    raise LexerError()

lexer = lex.lex()

def lex(data):
    lexer.input(data)
    # Tokenize
    tokens = []
    while True:
        tok = lexer.token()
        if not tok: 
            break      # No more input
        tokens.append(tok)
        pass
    return tokens


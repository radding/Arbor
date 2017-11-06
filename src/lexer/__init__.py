import ply.lex as lex

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
] + list(reserved.values())

t_INT = r'-?[0-9]+'
t_FLOAT = r'-?[0-9]*\.[0-9]+'
t_PLUS = r'\+'
t_MULTI = r'\*'
t_DIV = r'\/'
t_SUB = r'-'
# t_NAME = r'[a-zA-Z_]+([a-zA-Z0-9_])*'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COLON = r'\:'
t_COMMA = r'\,'
t_SEMICOLON = r'\;'
t_ARROW = r'\-\>'
t_EQ = r'='

t_ignore = ' \t'
def t_NAME(t):
    r'[a-zA-Z_]+([a-zA-Z0-9_])*'
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
    t.lexer.skip(1)
    pass

lexer = lex.lex()

def lex(data):
    lexer.input(data)
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: 
            break      # No more input
        print(tok)


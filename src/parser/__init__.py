import ply.yacc as yacc

from src.lexer import tokens

start = 's'

class ParserError(Exception):
    def __init__(self, p):
        self.p = p
        pass

def p_start(p):
    '''s : statements'''
    p[0] = p[1]

def p_empty(p):
    'empty : '
    pass

def p_statements(p):
    '''statements : statements statement
                   | empty'''
    if (p[1] is not None):
        p[0] = p[1] + [p[2], ]
        pass
    elif (len(p) >= 3):
        p[0] = [p[2], ]
    else:
        p[0] = []
        pass

def p_statement(p):
    '''statement : expression SEMICOLON
                 | empty'''
    p[0] = p[1]
    pass

def p_int(p):
    '''constant : INT'''
    p[0] = ['int', p[1]]
    pass

def p_float(p):
    '''constant : FLOAT'''
    p[0] = ['float', p[1]]
    pass

def p_constant(p):
    '''expression : constant'''
    p[0] = p[1]
    pass

def p_use(p):
    '''expression : NAME'''
    p[0] = p[1]
    pass

def p_bin_op(p):
    '''expression : expression PLUS expression
                  | expression SUB expression
                  | expression MULTI expression
                  | expression DIV expression'''
    p[0] = ['binop', p[1], p[2], p[3]]

def p_assignment(p):
    '''expression : NAME EQ expression
                  | decl EQ expression'''
    p[0] = ["assign", p[1], p[3]]
    
def p_decl(p):
    '''decl : CONST NAME
            | LET NAME'''
    p[0] = p[2]
    pass

def p_commaList(p):
    '''commas : param
              | param COMMA commas'''
    if (len(p) >= 4):
        p[0] = p[3] + [p[1], ]
        pass
    else:
        p[0] = [p[1], ]
        pass

def p_param(p):
    '''param : NAME'''
    p[0] = ['param', p[1]]
    pass

def p_type(p):
    '''type : INTTYPE
            | FLOATTYPE
            | CHARTYPE'''
    p[0] = p[1]
    pass

def p_paramTypeDef(p):
    '''paramtype : NAME COLON type'''
    p[0] = ['paramtype', p[1], p[3]]

def p_paramType(p):
    '''param : paramtype'''
    p[0] = p[1]
    pass

def p_defaultParam(p):
    '''param : NAME EQ constant
             | paramtype EQ constant'''
    p[0] = ["default", p[1], p[3]]
    pass

def p_list(p):
    '''paramlist : LPAREN commas RPAREN
                 | LPAREN RPAREN'''
    if (p[2] != ')'):
        p[0] = ["params", p[2], ]
        pass
    else:
        p[0] = None
    pass

def p_block(p):
    '''func_block : blockEnter statements DONE'''
    p[0] = ["block", p[2]]
    pass

# def p_blockToExpression(p):
#     '''statement : block'''
#     p[0] = p[1]
#     pass

def p_blockEnter(p):
    '''blockEnter : ARROW'''
    pass

def p_functionDef(p):
    '''constant : paramlist func_block'''
    p[0] = ["func", p[1], p[2]]
    pass

def p_if(p):
    '''statement : IF LPAREN expression RPAREN ifblock'''
    p[0] = ["if", p[3], p[5]]
    pass

def p_ifblock(p):
    '''ifblock : ifenter statements DONE'''
    p[0] = p[2]
    pass

def p_ifenter(p):
    '''ifenter : COLON'''
    pass
    
# def p_error(p):
#     raise ParserError(p)

parser = yacc.yacc(debug = True)

def parse(data):
    try:
        ast = parser.parse(data)
        print(ast)        
    except ParserError as p:
        print("Syntax error", "{0}:{1}:".format(p.p.lineno, find_column(data, p.p)), p.p.value)

def find_column(input, token):
    last_cr = input.rfind('\n',0,token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr)
    return column
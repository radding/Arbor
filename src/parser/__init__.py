import ply.yacc as yacc

from src.lexer import tokens
from src.ast import (
    IntNode,
    AddNode, 
    BaseNode,
    FunctionDefNode,
    FileNode,
    Context,
    AssignNode,
    ParamDefNode,
    UsageNode,
    DeclNode,
    ReturnNode,
    FloatNode,
    MinusNode,
    MultNode,
    DivNode,
)

start = 's'

typesToLLVM = {
    "int": "i32",
    "char":"i8",
    "float": "double",
}

class ParserError(Exception):
    def __init__(self, p):
        self.p = p
        pass

def p_start(p):
    '''s : statements'''
    Context.instance().pushScope()
    p[0] = FileNode(*p[1].children)
    pass

def p_empty(p):
    'empty : '
    pass

def p_statements(p):
    '''statements : statements statement
                   | empty'''
    if (p[1] is not None):
        child = p[1].children + (p[2], )
        pass
    elif (len(p) >= 3):
        child = [p[2], ]
    else:
        child = []
        pass
    p[0] = BaseNode(*child)
    pass

def p_statement(p):
    '''statement : expression SEMICOLON
                 | empty'''
    p[0] = p[1]
    pass

def p_booleanOps(p):
    '''expression : expression AND expression
                  | expression OR expression'''
    p[0] = ["bool", p[1], p[2], p[3]]
    pass

def p_not(p):
    '''expression : NOT expression'''
    p[0] = ["not", p[2]]
    pass

def p_int(p):
    '''constant : INT
                | HEX
                | OCT'''
    p[0] = IntNode(p[1])
    pass

def p_char(p):
    '''constant : CHAR'''
    p[0] = ["char", p[1]]
    pass

def p_float(p):
    '''constant : FLOAT'''
    p[0] = FloatNode(p[1])
    pass

def p_string(p):
    '''constant : STRING'''
    p[0] = ["array[char]", p[1]]
    pass

def p_constant(p):
    '''expression : constant'''
    p[0] = p[1]
    pass

def p_use(p):
    '''usage : NAME'''
    p[0] = UsageNode(p[1])
    pass

def p_funcUsage(p):
    '''usage : NAME LPAREN commas_param RPAREN'''
    p[0] = ["func use", p[1], p[3]]
    pass

def p_usage(p):
    '''expression : usage'''
    p[0] = p[1]
    pass

def p_declaration(p):
    '''expression : decl'''
    p[0] = p[1]
    pass

def p_return(p):
    '''expression : RETURN expression'''
    p[0] = ReturnNode(p[2])
    pass

def p_bin_op(p):
    '''expression : expression PLUS expression
                  | expression SUB expression
                  | expression MULTI expression
                  | expression DIV expression'''
    if (p[2] == '+'):
        p[0] = AddNode(p[1], p[3])
        pass
    elif(p[2] == '-'):
        p[0] = MinusNode(p[1], p[3])
        pass
    elif (p[2] == '*'):
        p[0] = MultNode(p[1], p[3])
        pass
    elif p[0] == '/':
        p[0] = DivNode(p[1], p[3])
        pass
    else:
        p[0] = ['binop', p[1], p[2], p[3]]
        pass

def p_assignment(p):
    '''expression : usage EQ expression
                  | decl EQ expression'''
    p[0] = AssignNode(p[1], p[3])
    pass
    
def p_decl(p):
    '''decl : LET NAME'''
    p[0] = DeclNode(p[2])
    pass

def p_constDecl(p):
    '''decl : CONST NAME'''
    p[0] = DeclNode(p[2], True)
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
    p[0] = ParamDefNode(p[1])
    pass

def p_paramUse(p):
    '''paramuse : NAME
                | constant
                | empty'''
    p[0] = p[1]
    pass

def p_paramList(p):
    '''commas_param : paramuse
                    | paramuse COMMA commas_param'''
    if (len(p) >= 4):
        p[0] = p[3] + [p[1], ]
        pass
    else:
        p[0] = [p[1], ]
        pass
    pass

def p_expressionParenth(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]
    pass

def p_type(p):
    '''type : INTTYPE
            | FLOATTYPE
            | CHARTYPE
            | FUNCTIONTYPE'''
    p[0] = typesToLLVM.get(p[1], "i32*")
    pass

def p_paramTypeDef(p):
    '''paramtype : NAME COLON type'''
    p[0] = ParamDefNode(p[1], p[2])
    pass

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
                 | LPAREN param RPAREN
                 | LPAREN RPAREN'''
    if (p[2] != ')'):
        p[0] = p[2]
        pass
    else:
        p[0] = None
    pass

def p_block(p):
    '''func_block : blockEnter statements DONE'''
    p[0] = p[2]
    pass

def p_comps(p):
    '''expression : expression EQCOMP expression
                  | expression LT expression
                  | expression LTE expression
                  | expression GT expression
                  | expression GTE expression
                  | expression NEQ expression''' 
    p[0] = ["comps", p[1], p[2], p[3]]
    pass

def p_blockEnter(p):
    '''blockEnter : ARROW'''
    Context.instance().pushScope()
    pass

def p_functionDef(p):
    '''function : paramlist func_block'''
    Context.instance().popScope()    
    p[0] = FunctionDefNode(p[1], p[2])
    pass

def p_expressionToFunction(p):
    '''expression : function'''
    p[0] = p[1]
    pass

def p_if(p):
    '''statement : IF LPAREN expression RPAREN ifblock'''
    p[0] = ["if", p[3], p[5]]
    pass

def p_if_else(p):
    '''statement : IF LPAREN expression RPAREN ifenter statements elseif'''
    p[0] = ["ifelse", p[3], p[6], p[7]]
    pass


def p_elseif(p):
    '''elseif : ELSE IF LPAREN expression RPAREN ifblock'''
    p[0] = ["elseif", p[4], p[6]]
    pass

def p_elseifelse(p):
    '''elseif : ELSE ifblock'''
    p[0] = ["else", p[2]]
    pass

def p_elseifelseif(p):
    '''elseif : ELSE IF LPAREN expression RPAREN ifenter statements elseif'''
    p[0] = ["elseif", p[4], p[7]] + p[8]
    pass


def p_ifblock(p):
    '''ifblock : ifenter statements DONE SEMICOLON'''
    p[0] = p[2]
    pass

def p_ifenter(p):
    '''ifenter : ARROW'''
    pass

def p_error(p):
    raise ParserError(p)

parser = yacc.yacc(debug = True)

def parse(data, reraise=False):
    try:
        ast = parser.parse(data)
        return ast      
    except ParserError as p:
        if p.p is None:
            print("Syntax error: EOF")
        else:
            print("Syntax error", "{0}:{1}:".format(p.p.lineno, find_column(data, p.p)), p.p.value)
        if reraise:
            raise
        pass

def find_column(input, token):
    last_cr = input.rfind('\n',0,token.lexpos)
    if last_cr < 0:
        last_cr = 0
    column = (token.lexpos - last_cr)
    return column
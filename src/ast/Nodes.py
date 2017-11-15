import string
import random
import collections

from .Exceptions import InvalidTypeException, NotDefinedException, RedefinedException, RedefiningConstant
from .context import Context

names = set()

instance = Context.instance()

def uniqueGlobalName():
    while True:
        name = "".join((random.choice(string.ascii_lowercase) for i in range(10)))
        while name in names:
            name = "".join((random.choice(string.ascii_lowercase) for i in range(10)))
            pass
        names.add(name)
        yield name
        pass
    pass

uniqueGlobalName = uniqueGlobalName()

def getUniqueGlobalName():
    return next(uniqueGlobalName)


def registers():
    reg = 1
    while True:
        yield reg
        reg += 1
        pass
    pass

registers = registers()

def getNextRegister():
    return next(registers)

class BaseNode:
    def __init__(self, *args):
        self.children = args
        pass

    def compile(self, compiler, *args):
        for i in self.children:
            i.compile(compiler)
            pass
        pass
               
    pass

class FileNode(BaseNode):
    def compile(self, compiler=None):
        if compiler is None:
            compiler = collections.deque()
            pass
        compiler.append("define i32 @main() {")
        instance.pushScope()
        super().compile(compiler)
        compiler.append("ret i32 0;")   
        instance.popScope()     
        compiler.append("}") 
        return compiler
        

class ConstantNode(BaseNode):
    tp = None
    llvmTp = None

    def __init__(self, value):
        self.value = value
        pass

    def compile(self, compiler, *args):
        return self.value, self.llvmTp

class IntNode(ConstantNode):
    tp = "int"
    llvmTp = "i32"
    pass

class FloatNode(ConstantNode):
    tp = "double"
    llvmTp = "double"
    pass

class CharNode(ConstantNode):
    tp = 'char'
    llvmTp = 'i8'

class BinOpNode(BaseNode):
    lexem = None
    llvmInstruction = None

    @classmethod
    def isTypeOf(cls, lexem):
        if lexem == cls.lexem:
            return True
        return False

    def __init__(self, leftExpression, rightExpression):
        self.left = leftExpression
        self.right= rightExpression
        pass

    def compile(self, compiler):
        left, llvmTpLeft = self.left.compile(compiler)
        right, llvmTpRight = self.right.compile(compiler)
        if llvmTpLeft != llvmTpRight:
            raise InvalidTypeException()
        register = "%{}".format(getNextRegister())
        compiler.append("{} = {} {} {}, {}".format(register, self.llvmInstruction, llvmTpLeft, left, right))
        return register, llvmTpLeft

class AddNode(BinOpNode):
    lexem = "+"
    llvmInstruction = "add"
    pass

class MinusNode(BinOpNode):
    lexem = '-'
    llvmInstruction = "sub"
    pass

class MultNode(BinOpNode):
    lexem = "*"
    llvmInstruction = "mul"
    pass

class DivNode(BinOpNode):
    lexem = '/'
    llvmInstruction = "sdiv"
    pass


class FunctionDefNode(BaseNode):
    def __init__(self, params, statements):
        self.params = params
        self.statements = statements

    def compile(self, compiler, name=None):
        anon = name is None
        if anon:
            name = getUniqueGlobalName()
            pass
        if self.params is None:
            params = ""
            pass
        else:
            params = []
            for param in self.params:
                param.compile(params)
                pass
            params = ",".join(params)
            pass
        defineFunc = "define fastcc i32 @{}({}) {{".format(name, params)
        statements = []
        self.statements.compile(statements)
        statemtents = "\n".join(statements)
        compiler.appendleft("}")
        compiler.appendleft("ret i32 0;")
        compiler.appendleft(statemtents)
        compiler.appendleft(defineFunc)
        return '@{}'.format(name), 'i32'

class ParamDefNode(BaseNode):
    def __init__(self, name, type='i32*'):
        self.name = name
        self.type = type
        pass

    def compile(self, compiler):
        compiler.append("{} %{}".format(self.type, self.name))
        return compiler
    pass


class AssignNode(BaseNode):
    def __init__(self, name, assign):
        self.name = name
        self.assign = assign

    def compile(self, compiler):
        if isinstance(self.assign, FunctionDefNode):
            self.assign.compile(compiler, self.name.name)
            pass
        else:
            val, llvmTp = self.assign.compile(compiler)          
            if isinstance(self.name, DeclNode):
                self.name.addDetails(type=llvmTp)
                self.name.compile(compiler)
                pass
            elif isinstance(self.name, UsageNode):
                if self.name.details["constant"]:
                    raise RedefiningConstant(self.name.name)
            if llvmTp != self.name.details["type"]:
                raise SyntaxError()
            compiler.append("store {} {}, {}* {}".format(llvmTp, val, self.name.details["type"], self.name.details["location"]))
            pass
        pass
        return self.name.details["location"], self.name.details["type"]
    pass

class DeclNode(BaseNode):
    def __init__(self, name, constant=False):
        if instance.resolve(name, True) is not None:
            raise RedefinedException(name)
        self.name = name
        regName = "%{}".format(getUniqueGlobalName())
        self.details = {"constant": constant, "location": regName, "type": "i32"}
        instance.addScoped(name, self.details)
        pass

    def addDetails(self, **kwargs):
        for key, value in kwargs.items():
            self.details[key] = value
            pass
        instance.addScoped(self.name, self.details)        
        pass

    def compile(self, compiler):
        compiler.append("{} = alloca {}".format(self.details['location'], self.details['type']))
        return self.details['location'], self.details['type']

class UsageNode(BaseNode):
    def __init__(self, name):
        if Context.instance().resolve(name) is None:
            raise NotDefinedException(name)
        self.name = name
        self.details = instance.resolve(name)
        pass

    def compile(self, compiler):
        reg = "%{}".format(getNextRegister())
        compiler.append("{} = load {}, i32* {}".format(reg, self.details['type'], self.details['location']))
        return reg, self.details['type']

class ReturnNode(BaseNode):
    def __init__(self, expression):
        self.expression = expression
        pass

    def compile(self, compiler):
        register, type = self.expression.compile(compiler)
        compiler.append("ret {} {}".format(type, register))
        pass



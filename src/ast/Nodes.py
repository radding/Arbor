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


def getRegisters():
    reg = 1
    while True:
        yield reg
        reg += 1
        pass
    pass

registers = getRegisters()

def resetRegs():
    global registers
    registers = getRegisters()
    
instance.onPush(resetRegs)

def getNextRegister():
    return next(registers)

moduleMap = {}

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
    def __init__(self, name, *args):
        super().__init__(*args)
        self.name = name
        instance.addGlobal('__ModuleName', name)
        pass

    def compile(self, compiler=None):
        if compiler is None:
            compiler = collections.deque()
            pass
        elif self.name is not None:
            compiler.name = self.name
            pass
        if compiler.moduleName == 'main':
            compiler.append("define i32 @main() {")
            instance.pushScope()
            pass
        super().compile(compiler)
        if compiler.moduleName == 'main':
            compiler.append("ret i32 0;")   
            instance.popScope()     
            compiler.append("}")
            pass
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
    llvmTp = "f64"
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
        register = "%{}".format(getUniqueGlobalName())
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

class ModuleUseNode(BaseNode):
    def __init__(self, name):
        self.name = name
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
            params = compiler.clone()
            for param in self.params:
                param.compile(params)
                pass
            params = ",".join(params)
            pass
        compiler.addToModuleMap(name, {'params': [i.type for i in self.params]})
        defineFunc = "define fastcc i32 @{}.{}({}) {{".format(compiler.moduleName, name, params)
        statements = []
        self.statements.compile(statements)
        statemtents = "\n".join(statements)
        compiler.appendleft("}")
        compiler.appendleft("ret i32 0;")
        compiler.appendleft(statemtents)
        compiler.appendleft(defineFunc)
        return '@{}'.format(name), 'function'

class ParamDefNode(BaseNode):
    def __init__(self, name, type='i32*'):
        self.name = name
        self.type = type
        details = {"constant": False, "location": name, "type": type, "isParam": True}
        instance.addScoped(name, details)
        pass

    def compile(self, compiler):
        compiler.append("{} %{}".format(self.type, self.name))
        return compiler
    pass


class AssignNode(BaseNode):
    def __init__(self, name, assign):
        self.name = name
        self.assign = assign
        pass

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
    def __init__(self, name, constant=False, type="i32"):
        if instance.resolve(name, True) is not None:
            raise RedefinedException(name)
        self.name = name
        regName = "%{}".format(getUniqueGlobalName())
        self.details = {"constant": constant, "location": regName, "type": type}
        instance.addScoped(name, self.details)
        pass

    def addDetails(self, **kwargs):
        for key, value in kwargs.items():
            self.details[key] = value
            pass
        pass

    def compile(self, compiler):
        compiler.append("{} = alloca {}".format(self.details['location'], self.details['type']))
        return self.details['location'], self.details['type']

class UsageNode(BaseNode):
    def __init__(self, name):
        self.name = name
        self.details = instance.resolve(name)
        if self.details is None:
            raise NotDefinedException(self.name)
        pass

    def compile(self, compiler):
        if self.details.get("isParam", False):
            return "%{}".format(self.name), self.details["type"]
        reg = "%{}".format(getUniqueGlobalName())
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

class FuncCallNode(BaseNode):
    def __init__(self, name, params):
        self.name = name
        self.params = params
        pass

    def compile(self, compiler):
        parmWTypes = []
        for i in self.params:
            reg, type = i.compile(compiler)
            parmWTypes.append(" ".join([type, reg]))
            pass
        params = ", ".join(parmWTypes)
        reg = "%{}".format(getUniqueGlobalName())
        callStatements = "{} = call i32 @{}.{}({})".format(reg, compiler.moduleName, self.name, params)
        compiler.append(callStatements)
        return reg, "i32"
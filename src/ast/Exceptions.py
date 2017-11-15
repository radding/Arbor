class ASTExeption(Exception): pass
class SyntaxException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class InvalidTypeException(ASTExeption): pass
class NotDefinedException(SyntaxException):
    def __init__(self, name):
        super().__init__("Name {} is not defined".format(name))
        pass

class RedefinedException(SyntaxException):
    def __init__(self, name):
        super().__init__("Name {} is defined".format(name))
        pass

class RedefiningConstant(SyntaxException):
    def __init__(self, name):
        super().__init__("Attempting to redefine constant {}".format(name))
        pass

from .lexer import lex
from .parser import parse

def compileArbor(fileName):
    with open(args.file) as fi:
        ast = parse(fi.read())
        pass
    compiledCode = ast.compile(CompileVisitor(fileName=args.file))
    print(compiledCode.moduleMap)
    ir = "\n".join(compiledCode)
    return ir
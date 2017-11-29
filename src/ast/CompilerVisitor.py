import collections
import os

class CompileVisitor:

    def __init__(self, moduleName=None, fileName=None):
        if fileName is not None:
            fileName = os.path.split(fileName)[1]
            pass
        self.fileName = fileName and fileName.replace(".ab", "")
        self.fileName = self.fileName and self.fileName.replace("/", ".")
        self.name = moduleName
        self.moduleMap = {}
        self.compiler = collections.deque()
        self.location = 0
        pass

    @classmethod
    def Clone(cls, oldCompiler, cloneCompiler=False):
        newCompiler = cls()
        newCompiler.fileName = oldCompiler.fileName
        newCompiler.name = oldCompiler.name
        newCompiler.compiler = oldCompiler.compiler if cloneCompiler else collections.deque()
        newCompiler.location = oldCompiler.location
        return newCompiler

    def clone(self, cloneCompiler=False):
        return CompileVisitor.Clone(self, cloneCompiler)

    @property
    def moduleName(self):
        return self.name or self.fileName
    
    def addToModuleMap(self, name, details):
        otherModules = self.moduleMap.get(name)
        if otherModules is None:
            self.moduleMap[name] = [details, ]
            pass
        else:
            self.moduleMap[name].append(details)
            pass

    def resolveFromModuleName(self, name):
        return self.moduleMap.get(name)

    def append(self, obj):
        self.compiler.append(obj)
        pass

    def appendleft(self, obj):
        self.compiler.appendleft(obj)
        pass

    def __iter__(self):
        return self

    def __next__(self):
        if self.location >= len(self.compiler):
            self.location = 0
            raise StopIteration
        nxt = self.compiler[self.location]
        self.location += 1
        return nxt




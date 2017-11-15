class Context:
    _instance = None

    def __init__(self, initWithScope=True):
        self.context = {"scope": []}
        if initWithScope:
           self.context["scope"].append(Context(False))
           pass
        pass
        pass
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            pass
        return cls._instance

    def addGlobal(self, name, value):
        self.context[name] = value
        pass

    def get(self, name):
        return self.context.get(name)

    def isInGlobalScope(self):
        return len(self.context['scope']) > 0

    def addScoped(self, name, value):
        self.context["scope"][-1].addGlobal(name, value)
        pass

    def pushScope(self):
        self.context["scope"].append(Context())
        pass

    def popScope(self):
        self.context["scope"].pop()
        pass
    
    def resolve(self, name, current=False):
        if current:
            scope = self.context["scope"][-1]
            return scope.get(name)
        else:
            for scope in reversed(self.context["scope"]):
                ctx = scope.get(name)
                if ctx is not None:
                    return ctx
                pass
            pass
        return None

        
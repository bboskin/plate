###############################
## Errors
###############################

class UnboundVariable(Exception):
    pass
class SyntaxError(Exception):
    pass
class CompileError(Exception):
    pass
class RuntimeError(Exception):
    pass
class AbsurdError(Exception):
    pass

##############################################
## Types, Values, and Expressions parent class
##############################################

class Type():
    def __init__(self):
        pass
    @classmethod
    def __eq__(self, v1, v2):
        raise v1 == v2

class Value():
    def __init__(self, v, ty : Type):
        self.value = v
        self.type : Type = ty

class Expr():
    def __init__(self, type : Type):
        self.type : Type = type


############################
## Environments
############################

class Environment():
    def __init__(self):
        self.vars = []

    def lookup(self, x) -> Value:
        for y, t, v in self.vars:
            if y == x:
                return v
        raise UnboundVariable(x)
    
    def extend(self, x : str, ty : Type, v : Value):
        self.vars = [[x, ty, v]] + self.vars
    
    def copy(self):
        e = Environment()
        e.vars = self.vars.copy()
        return e

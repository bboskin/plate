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


class Value():
    def __init__(self, v, ty):
        self.value = v
        self.type : Type = ty

class Expr():
    def __init__(self, type):
        self.type : Type = type

class Type(Expr):
    def __init__(self):
        pass

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

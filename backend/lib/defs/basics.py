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
    def __str__(self):
        return str(self.value)

class Expr():
    def __init__(self, type):
        self.type : Type = type
        self.typed = False
        self.normalized = False
    def __str__(self):
        return "Expr"

class Type(Expr):
    def __init__(self):
        self.typed = False
        self.normalized = False
    def __str__(self):
        return "Type"
    
class Variable(Expr):
    def __init__(self, v : str, t : Type=Type()):
        super().__init__(self, t)
        self.name = v
        self.type = t
        self.typed = True
        self.normalized = True
    def __str__(self):
        return f"(Var {self.name})"

############################
## Environments
############################

class Environment():
    def __init__(self):
        self.vars : list[(Variable, Value)]= []

    def __str__(self):
        return ",".join([f"{e[0]} : {e[1]}\n" for e in self.vars])
    
    def lookup(self, x : str) -> Value:
        for y, v in self.vars:
            if y.name == x:
                return v
        raise UnboundVariable(x)
    
    def extend(self, var : Variable, v : Value):
        self.vars = [(var, v)] + self.vars
    
    def copy(self):
        e = Environment()
        e.vars = self.vars.copy()
        return e
    
############################
## Contexts
############################


## associates variables
## to normalized and typechecked expressions
class Context():
    def __init__(self):
        self.vars : list[(Variable, Expr)]= []

    def __str__(self):
        return ",".join([f"{e[0]} : {e[1]}\n" for e in self.vars])
    
    def lookup(self, x : str) -> (Type, Expr):
        for y, e in self.vars:
            if y.name == x:
                assert e.normalized and e.typed
                return e
        raise UnboundVariable(x)
    
    def extend(self, var : Variable, e : Expr):
        assert e.normalized and e.typed
        self.vars = [(var, e)] + self.vars
    
    def copy(self):
        e = Context()
        e.vars = self.vars.copy()
        return e
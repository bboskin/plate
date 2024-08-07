try:
    from .basics import *
    from .types import *
    from .expressions import *
except:
    from basics import *
    from types import *
    from expressions import *

################################
## Basic Types
################################

class VNothing(Value):
    def __init__(self, type : Type = TMaybe(Type())):
        self.type : Type = type

class VNumber(Value):
    def __init__(self, v, ty : Type):
        self.value = v
        self.type : Type = ty
    def __str__(self):
        return str(self.value)

class VBoolean(Value):
    def __init__(self, v, type : Type=TBoolean()):
        self.value : bool = v
        self.type : Type = type

class VString(Value):
    def __init__(self, v, ):
        self.value : str = v
        self.type : Type = TString()


################################
## Polymorphic Types
################################

class VList(Value):
    def __init__(self, v, ty : Type):
        self.values : list[Value] = v
        self.type : Type = ty
    def __str__(self):
        return f"{[str(e) for e in self.values]}"

class VJust(Value):
    def __init__(self, v, ty : Type):
        self.value = v
        self.ty : Type = TMaybe(ty)


## Used for both Lambdas and ForAlls
class Closure(Value):
    def __init__(self, x : Variable, env : Environment, body : Expr):
        self.var : Variable = x
        self.env : Environment = env
        self.body : Expr = body

    def __str__(self):
        return f"(Closure {self.var} : {self.body})"

class U(Value):
    def __init__(self, level):
        self.value = level
        self.type : Type = TUniverse(level+1)

class Proof(Value):
    def __init__(self, v1 : Value):
        self.val : Value = v1

class Absurd(Value):
    def __init__(self):
        raise AbsurdError





nothing : VNothing = VNothing()
true    : VBoolean = VBoolean(True)
false   : VBoolean = VBoolean(False)

CONSTANTS = [
    nothing,
    true, false
    ]


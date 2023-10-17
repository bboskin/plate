try:
    from .basics import *
except:
    from basics import *
##########################
## Basic Types
##########################

class TNothing(Type):
    pass

class TBoolean(Type):
    pass

class TNum(Type):
    pass

class TRational(TNum):
    pass

class TInt(TRational):
    pass

class TNat(TInt):
    pass
    
class TString(Type):
    pass
    
def merge_numeric_types(t1, t2):
    if isinstance(t1, TNat) and isinstance(t2, TNat):
        return TNat()
    elif (not isinstance(t1, TRational)) and (not isinstance(t2, TRational)):
        return TInt()
    else:
        return TRational()
        
##########################
## Polymorphic Types
##########################

class TList(Type):
    def __init__(self, type):
        self.contents : Type = type

class TMaybe(Type):
    def __init__(self, type):
        super().__init__(self)
        self.type : Type = type

class TFunction(Type):
    def __init__(self, tin : Variable=Type, out : Type=Type):
        self.input : Variable = tin
        self.output : Type = out
    
    def __str__(self):
        return f"[{self.input} -> {self.output}]"

    @classmethod
    def __eq__(v1, v2):
        return False

def Multi_Arg_Function(ins : list[Variable], out : Type) -> TFunction:
    if len(ins) == 0:
        raise CompileError
    elif len(ins) == 1:
        return TFunction(ins[0], out)
    else:
        return TFunction(ins[0], Multi_Arg_Function(ins[1:]))

    


##########################
## Dependent Types
##########################

class TUniverse(Type):
    def __init__(self, n : Expr):
        self.level = n
    @classmethod
    def __eq__(self, v1, v2):
        v1 : TUniverse = v1
        v2 : TUniverse = v2
        return v1.level == v2.level

class TEqual(Type):
    def __init__(self, ty : Type, e1 : Expr, e2 : Expr):
        self.type = ty
        self.lhs = e1
        self.rhs = e2

class TExists(Type):
    def __init__(self, x : str, x_ty : Type, p : Type):
        self.var = x
        self.var_type = x_ty
        self.prop = p

class TForAll(Type):
    def __init__(self, var : Variable, p : Type):
        self.var : Variable = var
        self.prop = p

class TAbsurd(Type):
    def __init__(self):
        self.type = TUniverse(0)
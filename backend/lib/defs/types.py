try:
    from .basics import *
except:
    from basics import *
##########################
## Basic Types
##########################

class TBoolean(Type):
    def __init__(self, type=Type()):
        self.type = type
        self.typed = False
        self.normalized = False
    def __str__(self):
        return "Boolean"

class TNum(Type):
    def __init__(self, type=Type()):
        self.type = type
        self.typed = False
        self.normalized = False
    def __str__(self):
        return "Num"

class TRational(TNum):
    def __str__(self):
        return "Rational"

class TInt(TRational):
    def __str__(self):
        return "Int"

class TNat(TInt):
    def __str__(self):
        return "Nat"
    
class TString(Type):
    def __init__(self, type=Type()):
        self.type = type
        self.typed = True
        self.normalized = True
    def __str__(self):
        return "String"
    

    
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
    def __init__(self, con_ty, ty=Type()):
        self.contents : Type = con_ty
        self.type : Type = ty
        self.normalized = False
        self.typed = False
    def __str__(self):
        return f"List[{self.contents}]"

class TMaybe(Type):
    def __init__(self, subtype, ty=Type()):
        self.subtype : Type = subtype
        self.type  : Type = ty
        self.typed = False
        self.normalized = False
    def __str__(self):
        return f"Maybe[{self.type}]"

class TFunction(Type):
    def __init__(self, tin : Variable, out : Type=Type(), type=Type()):
        self.input : Variable = tin
        self.output : Type = out
        self.type = type
        self.normalized = False
        self.typed = False
    
    def __str__(self):
        return f"({self.input} -> {self.output})"

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

class TEither(Type):
    def __init__(self, left, right, type=Type()):
        self.left = left
        self.right = right
        self.type = type
        self.normalized = False
        self.typed = False
    def __str__(self):
        return "Either"
    
class TUniverse(Type):
    def __init__(self, n : Expr, type=Type()):
        self.level : Expr = n
        self.type = type
        self.normalized = False
        self.typed = False
    def __str__(self):
        return f'(Universe {self.level})'

class TEqual(Type):
    def __init__(self, ty : Type, e1 : Expr, e2 : Expr):
        self.type = ty
        self.lhs = e1
        self.rhs = e2
    def __str__(self):
        return f'(Equal {self.lhs} {self.rhs})'

class TExists(Type):
    def __init__(self, x : str, x_ty : Type, p : Type):
        self.var = x
        self.var_type = x_ty
        self.prop = p
    def __str__(self):
        return f'(Exists {self.var} {self.prop})'

class TForAll(Type):
    def __init__(self, var : Variable, p : Type, ty=TUniverse(Literal(0, TNat()))):
        self.input : Variable = var
        self.output : Type = p
        self.type : Type = ty
    def __str__(self):
        return f"ForAll {self.var} : {self.prop}"

class TAbsurd(Type):
    def __init__(self, type=Type()):
        self.type = type
    def __str__(self):
        return f'Absurd'
from .basics import Type, Expr

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
    
##########################
## Polymorphic Types
##########################

class TList(Type):
    def __init__(self, type):
        self.contents : Type = type

    @classmethod
    def __eq__(self, v1, v2):
        if len(v1) != len(v2):
            return False
        else:
            cmp = self.contents.__eq__
            for i in range(len(v1)):
                if not cmp(v1[i], v2[i]):
                    return False
            return True
        

class TMaybe(Type):
    def __init__(self, type):
        super().__init__(self)
        self.type : Type = type
    
    @classmethod
    def __eq__(self, v1, v2):
        if v1 and v2:
            self.type.__eq__(v1, v2)
        elif not v1 and not v2:
            return True
        else:
            return False

class TFunction(Type):
    def __init__(self, ins : list[Type], out : Type):
        if len(ins) == 0:
            self.input : Type | None = None
            self.output : Type = out
        elif len(ins) == 1:
            self.input = ins[0]
            self.output = out
        else:
            self.input = ins[0]
            self.output = TFunction(ins[1:], out)

    @classmethod
    def __eq__(v1, v2):
        return False


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
    def __init__(self, x : str, x_ty : Type, p : Type):
        self.var = x
        self.var_type = x_ty
        self.prop = p

class TAbsurd(Type):
    def __init__(self):
        self.type = TUniverse(0)
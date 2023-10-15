try:
    from .basics import *
    from .types import *
except:
    from basics import *
    from types import *
################################
## Basic Programming Structures
################################

class Variable(Expr):
    def __init__(self, v : str, t : Type=Type()):
        self.name = v
        self.type = t

class Literal(Expr):
    def __init__(self, v, ty):
        self.val = v
        self.type : Type = ty


class ENothing(Literal):
    def __init__(self, type : Type=TNothing()):
        self.type : Type = type

class Let(Expr):
    def __init__(self, var : Variable, bind : Expr, body : Expr):
        self.var = var
        self.bind = bind
        self.body = body
        self.type = body.type


class Lambda(Expr):
    def __init__(self, var : Variable, body : Expr):
        self.var : Variable = var
        self.body : Expr = body
        self.type = TFunction(var.type, body.type)

class Application(Expr):
    def __init__(self, rator : Expr, rand : Expr):
        self.operator : Expr = rator
        self.operand : Expr = rand
        if not isinstance(rator.type, TFunction):
            raise CompileError(f"Expected a function at application, got {rator.type}")
        self.type = rator.type.output

class PrintThen(Expr):
    def __init__(self, message : str, e : Expr):
        self.message : str = message
        self.body : Expr = e
        self.type = e.type

##############################
## Numbers
##############################

class Plus(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type = merge_numeric_types(e1.type, e2.type)

class Times(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2

class Divide(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2

class Mod(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2


##############################
## Booleans
##############################

class If(Expr):
    def __init__(self, condition : Expr, consequent : Expr, else_expr : Expr, ty : Type=Type()):
        self.test : Expr = condition
        self.consequent : Expr = consequent
        self.else_expr : Expr = else_expr
        self.type : Type = ty

class Or(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = TBoolean()

class And(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = TBoolean()

class Not(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = TBoolean()

##############################
## Strings
##############################

class Concat(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type = TString()

class Contains(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type = TBoolean()


##############################
## Lists
##############################

class Append(Expr):
    def __init__(self, e1 : Expr, e2 : Expr, ty : Type):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = ty

class Empty(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = TBoolean()

class Car(Expr):
    def __init__(self, e1 : Expr, ty : Type=Type()):
        self.e1 : Expr = e1
        self.type : Type = ty

class Cdr(Expr):
    def __init__(self, e1 : Expr, ty : Type=Type()):
        self.e1 : Expr = e1
        self.type = ty

class Length(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type = TNat()

#####################
## Maybe
#####################

class Just(Expr):
    def __init__(self, e1 : Expr, ty : Type=Type()):
        self.e1 : Expr = e1
        self.type = TMaybe(ty)

#####################
## Dependent Types
#####################

class Refl(Expr):
    def __init__(self, val : Expr, ty : Type):
        self.val : Expr = val
        self.type : Type = ty

class Symm(Expr):
    def __init__(self, e : Expr, ty : TEqual):
        self.body = e
        self.ty = TEqual(ty.type, ty.rhs, ty.lhs)

class Look(Expr):
    def __init__(self, e : Expr, proof : Expr, type : Type):
        self.element : Expr = e
        self.proof : Expr = proof
        self.type : Type = type


####################
## Definitions
####################

class Def(Expr):
    pass

class Defunc(Def):
    def __init__(self, name : str, type : TFunction, body : Expr):
        self.name = name
        self.type : TFunction = type
        self.body : Expr = body

class Defconst(Def):
    def __init__(self, name : str, e : Expr):
        self.name : str = name
        self.body : Expr = e
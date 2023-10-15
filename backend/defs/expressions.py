from .basics import *
from .types import *
################################
## Basic Programming Structures
################################

class Defunc(Expr):
    def __init__(self, name : str, args : [str], arg_types : [Type], out : Type, body : list[Expr]):
        self.name = name
        self.args : dict[str : Type] = dict({a : t for a, t in zip(args, arg_types)})
        self.output : Type = out
        self.body : Expr = Expr

class Variable(Expr):
    def __init__(self, v : str, t : Type):
        self.var = v
        self.type = t

class Literal(Expr):
    def __init__(self, v, ty):
        self.val = v
        self.type : Type = ty


class ENothing(Expr):
    def __init__(self, type : Type=TNothing()):
        self.type : Type = type


class Let(Expr):
    def __init__(self, var : str, var_ty : Type, bind : Expr, body : Expr):
        self.var = var
        self.var_type = var_ty
        self.bind = bind
        self.body = body


class Lambda(Expr):
    def __init__(self, var : str, var_ty : Type, body : Expr):
        self.var : str = var
        self.var_type : Type = var_ty
        self.body : Expr = body

class Application(Expr):
    def __init__(self, rator : Expr, rand : Expr):
        self.operator : Expr = rator
        self.operand : Expr = rand

class PrintThen(Expr):
    def __init__(self, message : str, e : Expr):
        self.message : str = message
        self.body : Expr = e

##############################
## Numbers
##############################

class Plus(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2

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
    def __init__(self, type : Type, conditions : list[Expr], consequents : list[Expr], else_expr : Expr):
        self.cases = dict({cond : cons for cond, cons in zip(conditions, consequents)})
        self.type : Type = type
        self.else_expr : Expr = else_expr

class Or(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2

class And(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2

class Not(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1

##############################
## Strings
##############################

class Concat(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2

class Contains(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2


##############################
## Lists
##############################

class Append(Expr):
    def __init__(self, ty : Type, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = ty

class IsNull(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = TBoolean()

class Car(Expr):
    def __init__(self, ty : Type, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = ty

class Cdr(Expr):
    def __init__(self, ty : Type, e1 : Expr):
        self.e1 : Expr = e1
        self.type = ty

#####################
## Maybe
#####################

class Just(Expr):
    def __init__(self, ty : Type, e1 : Expr):
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
    def __init__(self, type : Type, e : Expr, proof : Expr):
        self.element : Expr = e
        self.proof : Expr = proof
        self.type : Type = type
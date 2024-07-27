try:
    from .basics import *
    from .types import *
except:
    from basics import *
    from types import *


## TODO implement explicit typecasting between nums, and to boolean


################################
## Basic Programming Structures
################################



class ENothing():
    def __init__(self, type : Type=Type()):
        self.type : Type = type
        self.normalized = False
        self.typed = False

    def __str__(self):
        return "nothing"

class QED(Expr):
    def __init__(self):
        self.typed = False
        self.normalized = False
    def __str__(self):
        return "QED"
    
class Let(Expr):
    def __init__(self, var : Variable, bind : Expr, b : Expr):
        self.var = var
        self.bind = bind
        self.body = b
        self.type = b.type
        self.normalized = False
        self.typed = False


    def __str__(self):
        return f"(let {self.var} be {self.bind} in {self.body})"


class Lambda(Expr):
    def __init__(self, vars : [Variable], body : Expr):
        self.var : Variable = vars[0]
        if len(vars) > 1:
            self.body : Expr = Lambda(vars[1:], body)
        else:
            self.body : Expr = body
        self.type = TForAll(vars[0], self.body.type)
        self.normalized = False
        self.typed = False
        # print(f"Constructed a lambda {self} with {self.type}")
    def __str__(self):
        return f"(lambda {self.var} : {self.body})"

class Application(Expr):
    def __init__(self, rator : Expr, rand : Expr):
        self.operator : Expr = rator
        self.operand : Expr = rand
        self.type : Type = rator.type
        self.normalized = False
        self.typed = False
    
    def __str__(self):
        return f"({self.operator} {self.operand})"

class PrintThen(Expr):
    def __init__(self, message : str, e : Expr):
        self.normalized = False
        self.typed = False
        self.message : str = message
        self.body : Expr = e
        self.type = e.type
    
    def __str__(self):
        return f"(print {self.message} {self.body})"

##############################
## Numbers
##############################

class Plus(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type = merge_numeric_types(e1.type, e2.type)
        self.normalized = False
        self.typed = False
    def __str__(self):
        return f"({self.e1} + {self.e2})"
    
class Max(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type = merge_numeric_types(e1.type, e2.type)
        self.normalized = False
        self.typed = False
    def __str__(self):
        return f"(max {self.e1}, {self.e2})"

class Min(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type = merge_numeric_types(e1.type, e2.type)
        self.normalized = False
        self.typed = False
    def __str__(self):
        return f"(min {self.e1}, {self.e2})"

class Times(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = merge_numeric_types(e1.type, e2.type)
        self.normalized = False
        self.typed = False
    def __str__(self):
        return f"({self.e1} * {self.e2})"

class Divide(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
    def __str__(self):
        return f"({self.e1} / {self.e2})"

class Mod(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Expr = TNat()
    def __str__(self):
        return f"({self.e1} % {self.e2})"


##############################
## Booleans
##############################

class If(Expr):
    def __init__(self, condition : Expr, consequent : Expr, else_expr : Expr, ty : Type=Type()):
        self.test : Expr = condition
        self.consequent : Expr = consequent
        self.else_expr : Expr = else_expr
        self.type : Type = ty
        self.normalized = False
        self.typed = False
    
    def __str__(self):
        return f"(if {self.test} then {self.consequent} else {self.else_expr})"

class Or(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = TBoolean()
        self.normalized = False
        self.typed = False

    def __str__(self):
        return f"({self.e1} or {self.e2})"

class And(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = TBoolean()
        self.normalized = False
        self.typed = False

    def __str__(self):
        return f"({self.e1} and {self.e2})"

class Not(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = TBoolean()
        self.normalized = False
        self.typed = False
    def __str__(self):
        return f"(not {self.e1})"

class Equal(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = TBoolean()
        self.normalized = False
        self.typed = False
    
    def __str__(self):
        return f"({self.e1} == {self.e2})"

##############################
## Strings
##############################

class Concat(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type = TString()
        self.normalized = False
        self.typed = False

    def __str__(self):
        return f"({self.e1} ++ {self.e2})"

class Contains(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type = TBoolean()
        self.normalized = False
        self.typed = False

    def __str__(self):
        return f"({self.e1} in {self.e2})"


##############################
## Lists
##############################

class Append(Expr):
    def __init__(self, e1 : Expr, e2 : Expr, ty : Type):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = ty
        self.normalized = False
        self.typed = False

    def __str__(self):
        return f"({self.e1} + {self.e2})"

class Empty(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = TBoolean()
        self.normalized = False
        self.typed = False
    
    def __str__(self):
        return f"(empty {self.e1})"



class Length(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type = TNat()

    def __str__(self):
        return f"(length {self.e1})"

class Member(Expr):
    def __init__(self, e1 :Expr, e2 : Expr):

        self.value = e1
        self.list = e2
        self.type = TBoolean()
        self.normalized = False
        self.typed = False

    def __str__(self):
        return f"({self.value} in {self.list})"
    
class List(Expr):
    def __init__(self, es  : list[Expr], type : Type=TList(Type())):

        self.values : list[Expr] = es
        self.type : Type = type
        self.normalized = False
        self.typed = False
    
    def __str__(self):
        return "(List: [" + ",".join([str(v) for v in self.values]) + "])"

#####################
## Maybe
#####################

class Just(Expr):
    def __init__(self, e1 : Expr, ty : Type=Type()):
        self.e1 : Expr = e1
        self.type = TMaybe(ty)
        self.normalized = False
        self.typed = False

    def __str__(self):
        return f"(just {self.e1})"

#####################
## Dependent Types
#####################

class Induct(Expr):
    def __init__(self, arg : Expr, out_type : Expr, base : Expr, inds : [Expr], type : Type=Type()):
        self.arg : Expr = arg
        self.out_type : Type = out_type
        self.base : Expr = base
        self.inds : [Expr] = inds
        self.type : Type = type
        self.normalized = False
        self.typed = False
    def __str__(self):
        return f"(induct {self.arg} : {self.type} -> {self.out_type})"

class Refl(Expr):
    def __init__(self, val : Expr, ty : Type):
        self.val : Expr = val
        self.type : Type = ty
        self.normalized = False
        self.typed = False

    def __str__(self):
        return f"(same {self.val})"

class Symm(Expr):
    def __init__(self, e : Expr, ty : TEqual):
        self.body = e
        self.ty : TEqual = ty
        self.normalized = False
        self.typed = False

    def __str__(self):
        return f"(symm {self.body})"
    
class Trans(Expr):
    def __init__(self, e1 : Expr, e2 : Expr, ty : TEqual):
        self.e1 = e1
        self.e2 = e2
        self.ty = ty
        self.normalized = False
        self.typed = False

    def __str__(self):
        return f"(trans {self.e1} = {self.e2})"
    
class Cong(Expr):
    def __init__(self, f : Expr, e : Expr, ty : TEqual):
        self.fn = f
        self.e1 = e
        self.ty = ty
        self.normalized = False
        self.typed = False

    def __str__(self):
        return f"(cong {self.fn} {self.e1})"

class Look(Expr):
    def __init__(self, e : Expr, proof : Expr, type : Type):
        self.element : Expr = e
        self.proof : Expr = proof
        self.type : Type = type
        self.normalized = False
        self.typed = False
    
    def __str__(self):
        return f"(look {self.element} : {self.proof})"

class Car(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = Type()
        self.normalized = False
        self.typed = False
    
    def __str__(self):
        return f"(car {self.e1})"
    
class Cdr(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = Type()
        self.normalized = False
        self.typed = False
    
    def __str__(self):
        return f"(cdr {self.e1})"
    
class Left(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = Type()
        self.normalized = False
        self.typed = False
    
    def __str__(self):
        return f"(left {self.e1})"

class Right(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = Type()
        self.normalized = False
        self.typed = False
    
    def __str__(self):
        return f"(right {self.e1})"

####################
## Definitions
####################

class Def(Expr):
    pass

class Defunc(Def):
    def __init__(self, var : Variable, body : Expr):
        self.var : Variable = var
        self.body : Expr = body

    def __str__(self):
        return f"(defunc {self.var} : {self.body})"

class Defconst(Def):
    def __init__(self, var : Variable, e : Expr):
        self.var : str = var
        self.body : Expr = e

    def __str__(self):
        return f"(defconst {self.var} : {self.body})"
    
class Defrel(Def):
    def __init__(self, var : Variable, e : Expr):
        self.var : Variable = var
        self.body : Expr = e
    def __str__(self):
        return f"(defrel {self.var} {self.body})"
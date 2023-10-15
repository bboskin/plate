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
    def __str__(self):
        return f"[{self.name} : {self.type}]"

class Literal(Expr):
    def __init__(self, v, ty):
        self.val = v
        self.type : Type = ty
    def __str__(self):
        return f"{self.val}"


class ENothing(Literal):
    def __init__(self, type : Type=TNothing()):
        self.type : Type = type
    
    def __str__(self):
        return "nothing"

class Let(Expr):
    def __init__(self, var : Variable, bind : Expr, b : Expr):
        self.var = var
        self.bind = bind
        self.body = b
        self.type = b.type

    def __str__(self):
        return F"let {self.var} be {self.bind} in {self.body}"


class Lambda(Expr):
    def __init__(self, var : Variable, body : Expr):
        self.var : Variable = var
        self.body : Expr = body
        self.type = TFunction(var.type, body.type)

    def __str__(self):
        return F"lambda {self.var} : {self.body}"

class Application(Expr):
    def __init__(self, rator : Expr, rand : Expr):
        self.operator : Expr = rator
        self.operand : Expr = rand
        if not isinstance(rator.type, TFunction):
            raise CompileError(f"Expected a function at application, got {rator.type}")
        self.type = rator.type.output
    
    def __str__(self):
        return f"{self.operator}({self.operand})"

class PrintThen(Expr):
    def __init__(self, message : str, e : Expr):
        self.message : str = message
        self.body : Expr = e
        self.type = e.type
    
    def __str__(self):
        return f"print {self.message}, {self.body}"

##############################
## Numbers
##############################

class Plus(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type = merge_numeric_types(e1.type, e2.type)

    def __str__(self):
        return f"{self.e1} + {self.e2}"

class Times(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
    def __str__(self):
        return f"{self.e1} * {self.e2}"

class Divide(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
    def __str__(self):
        return f"{self.e1} / {self.e2}"

class Mod(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
    def __str__(self):
        return f"{self.e1} % {self.e2}"


##############################
## Booleans
##############################

class If(Expr):
    def __init__(self, condition : Expr, consequent : Expr, else_expr : Expr, ty : Type=Type()):
        self.test : Expr = condition
        self.consequent : Expr = consequent
        self.else_expr : Expr = else_expr
        self.type : Type = ty
    
    def __str__(self):
        return f"if {self.test} then {self.consequent} else {self.else_expr}"

class Or(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = TBoolean()

    def __str__(self):
        return f"{self.e1} or {self.e2}"

class And(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = TBoolean()

    def __str__(self):
        return f"{self.e1} and {self.e2}"

class Not(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = TBoolean()
    def __str__(self):
        return f"not {self.e1}"

##############################
## Strings
##############################

class Concat(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type = TString()

    def __str__(self):
        return f"{self.e1} ++ {self.e2}"

class Contains(Expr):
    def __init__(self, e1 : Expr, e2 : Expr):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type = TBoolean()

    def __str__(self):
        return f"{self.e1} in {self.e2}"


##############################
## Lists
##############################

class Append(Expr):
    def __init__(self, e1 : Expr, e2 : Expr, ty : Type):
        self.e1 : Expr = e1
        self.e2 : Expr = e2
        self.type : Type = ty

    def __str__(self):
        return f"{self.e1} + {self.e2}"

class Empty(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type : Type = TBoolean()
    
    def __str__(self):
        return f"empty {self.e1}"

class Car(Expr):
    def __init__(self, e1 : Expr, ty : Type=Type()):
        self.e1 : Expr = e1
        self.type : Type = ty

    def __str__(self):
        return f"car {self.e1}"

class Cdr(Expr):
    def __init__(self, e1 : Expr, ty : Type=Type()):
        self.e1 : Expr = e1
        self.type = ty

    def __str__(self):
        return f"cdr {self.e1}"

class Length(Expr):
    def __init__(self, e1 : Expr):
        self.e1 : Expr = e1
        self.type = TNat()

    def __str__(self):
        return f"length {self.e1}"

class In(Expr):
    def __init__(self, e1 :Expr, e2 : Expr):
        self.value = e1
        self.list = e2
        self.type = TBoolean()

    def __str__(self):
        return f"{self.value} in {self.list}"

#####################
## Maybe
#####################

class Just(Expr):
    def __init__(self, e1 : Expr, ty : Type=Type()):
        self.e1 : Expr = e1
        self.type = TMaybe(ty)

    def __str__(self):
        return f"just {self.e1}"

#####################
## Dependent Types
#####################

class Refl(Expr):
    def __init__(self, val : Expr, ty : Type):
        self.val : Expr = val
        self.type : Type = ty

    def __str__(self):
        return f"same {self.val}"

class Symm(Expr):
    def __init__(self, e : Expr, ty : TEqual):
        self.body = e
        self.ty = TEqual(ty.type, ty.rhs, ty.lhs)

    def __str__(self):
        return f"symm {self.body}"

class Look(Expr):
    def __init__(self, e : Expr, proof : Expr, type : Type):
        self.element : Expr = e
        self.proof : Expr = proof
        self.type : Type = type
    
    def __str__(self):
        return f"look {self.element} : {self.proof}"


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

    def __str__(self):
        return f"defunc {self.name} : {self.type}: {self.body}"

class Defconst(Def):
    def __init__(self, name : str, e : Expr):
        self.name : str = name
        self.body : Expr = e

    def __str__(self):
        return f"defconst {self.name} : {self.body}"
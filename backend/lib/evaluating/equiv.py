from defs import *

class Lex(Expr):
    def __init__(self, i : int):
        self.name : int = i
        
## converting variable to lexical address for
def vars_to_lex(e : Expr, old : str, new : int):
    raise NotImplementedError


## TODO write alpha equivalence for expressions
def alpha_equiv(e1 : Expr, e2 : Expr, τ : Type, lex_idx=0) -> bool:
    raise NotImplementedError


## TODO subtyping (numeric types only for right now)
def is_numeric_subtype(τ1 : Type, τ2 : type) -> bool:
    raise NotImplementedError
from ..defs import *
from loguru import logger
## TODO write alpha equivalence for expressions
def alpha_equiv(e : Expr, e2 : Expr, lex_env : list[Environment]= [Environment(), Environment()], lex_addr=0) -> bool:
    ## Prints do not contribute to alpha
    # logger.debug(e)
    # logger.debug(e2)
    if isinstance(e, PrintThen):
        return alpha_equiv(e.body, e2, lex_env, lex_addr)
    elif isinstance(e2, PrintThen):
        return alpha_equiv(e, e2.body, lex_env, lex_addr)
    elif isinstance(e, Variable):
        if not isinstance(e2, Variable):
            return False
        try:
            e_i = lex_env[0].lookup(e.name)
            e_bound = True
        except:
            e_bound = False
        try:
            e2_i = lex_env[1].lookup(e2.name)
            e2_bound = True
        except:
            e2_bound = False
        if (not e_bound) or (not e2_bound):
            if e_bound or e2_bound:
                return False
            return e.name == e2.name
        return e_i == e2_i
    elif isinstance(e, Literal):
        return isinstance(e2, Literal) and e.val == e2.val
    if isinstance(e, Lambda):
        if not isinstance(e2, Lambda):
            return False
        else:
            lex_env[0].extend(e.var, lex_addr)
            lex_env[1].extend(e2.var, lex_addr)
            return alpha_equiv(e.body, e2.body, lex_env, lex_addr+1)
    elif isinstance(e, List):
        if not isinstance(e2, List):
            return False
        if not (len(e.values) == len(e2.values)):
            return False
        else:
            for i in range(len(e.values)):
                if not alpha_equiv(e.values[i], e2.values[i], lex_env, lex_addr):
                    return False
            return True
    
    ## Numbers
    elif isinstance(e, Plus):
        return isinstance(e2, Plus) and \
            alpha_equiv(e.e1, e2.e1, lex_env, lex_addr) and \
            alpha_equiv(e.e2, e2.e2, lex_env, lex_addr)
    elif isinstance(e, Times):
        return isinstance(e2, Times) and \
            alpha_equiv(e.e1, e2.e1, lex_env, lex_addr) and \
            alpha_equiv(e.e2, e2.e2, lex_env, lex_addr)

    ## Booleans
    elif isinstance(e, If):
        return isinstance(e2, If) and \
            alpha_equiv(e.test, e2.test, lex_env, lex_addr) and \
                alpha_equiv(e.consequent, e2.consequent, lex_env, lex_addr) and \
                alpha_equiv(e.else_expr, e2.else_expr, lex_env, lex_addr)

    elif isinstance(e, Or):
        return isinstance(e2, Or) and \
            alpha_equiv(e.e1, e2.e1, lex_env, lex_addr) and \
            alpha_equiv(e.e2, e2.e2, lex_env, lex_addr)
    elif isinstance(e, And):
        return isinstance(e2, And) and \
            alpha_equiv(e.e1, e2.e1, lex_env, lex_addr) and \
            alpha_equiv(e.e2, e2.e2, lex_env, lex_addr)
    elif isinstance(e, Not):
        return isinstance(e2, Not) and \
            alpha_equiv(e.e1, e2.e1, lex_env, lex_addr)
    elif isinstance(e, Equal):
        return isinstance(e2, Equal) and \
            alpha_equiv(e.e1, e2.e1, lex_env, lex_addr) and \
            alpha_equiv(e.e2, e2.e2, lex_env, lex_addr)

    ## Strings
    elif isinstance(e, Concat):
        return isinstance(e2, Concat) and \
            alpha_equiv(e.e1, e2.e1, lex_env, lex_addr) and \
            alpha_equiv(e.e2, e2.e2, lex_env, lex_addr)
    elif isinstance(e, Contains):
        return isinstance(e2, Contains) and \
            alpha_equiv(e.e1, e2.e1, lex_env, lex_addr) and \
            alpha_equiv(e.e2, e2.e2, lex_env, lex_addr)

    ## Lists
    elif isinstance(e, Append):
        return isinstance(e2, Append) and \
            alpha_equiv(e.e1, e2.e1, lex_env, lex_addr) and \
            alpha_equiv(e.e2, e2.e2, lex_env, lex_addr)
    elif isinstance(e, Empty):
        return isinstance(e2, Empty) and \
            alpha_equiv(e.e1, e2.e1, lex_env, lex_addr)
    elif isinstance(e, Member):
        return isinstance(e2, Member) and \
            alpha_equiv(e.list, e2.list, lex_env, lex_addr) and \
            alpha_equiv(e.value, e2.value, lex_env, lex_addr)
    elif isinstance(e, Length):
        return isinstance(e2, Length) and \
            alpha_equiv(e.e1, e2.e1, lex_env, lex_addr)

    ## Environment Mutation
    elif isinstance(e, Let):
        if not isinstance(e2, Let):
            return False
        if not alpha_equiv(e.bind, e2.bind, lex_env, lex_addr):
            return False
        lex_env[0].extend(e.var, lex_addr)
        lex_env[1].extend(e2.var, lex_addr)
        return alpha_equiv(e.body, e2.body, lex_env, lex_addr+1)
    elif isinstance(e, Application):
        return isinstance(e2, Application) and \
            alpha_equiv(e.operator, e2.operator, lex_env, lex_addr) and \
            alpha_equiv(e.operand, e2.operand, lex_env, lex_addr)

    ## dependent types
    elif isinstance(e, Induct):
        check = isinstance(e2, Induct) and \
            alpha_equiv(e.arg, e2.arg, lex_env, lex_addr) and \
            alpha_equiv(e.base, e2.base, lex_env, lex_addr) and \
            alpha_equiv(e.type, e2.type, lex_env, lex_addr) and \
            (len(e.inds) == len(e2.inds))
        if not check:
            return False
        for i in range(len(e.inds)):
            if not alpha_equiv(e.inds[i], e2.inds[i], lex_env, lex_addr):
                return False
        return True
        
    ## cases from check
    elif isinstance(e, ENothing):
        return isinstance(e2, ENothing)
    elif isinstance(e, Just):
        return isinstance(e2, Just) and alpha_equiv(e.e1, e2.e1)
    elif isinstance(e, Refl):
        return isinstance(e2, Refl) and alpha_equiv(e.val, e2.val)
    elif isinstance(e, Symm):
        return isinstance(e2, Symm) and alpha_equiv(e.body, e2.body)
    elif isinstance(e, Trans):
        return isinstance(e2, Trans) and alpha_equiv(e.e1, e2.e1) and alpha_equiv(e.e2, e2.e2)
    elif isinstance(e, Cong):
        return isinstance(e2, Cong) and alpha_equiv(e.fn, e2.fn) and alpha_equiv(e.e1, e2.e1)
    elif isinstance(e, Look):
        return isinstance(e2, Look) and alpha_equiv(e.element, e2.element) and alpha_equiv(e.proof, e2.proof)
    

    ## Types
    elif isinstance(e, TUniverse):
        return isinstance(e2, TUniverse) and \
            alpha_equiv(e.level, e2.level, lex_env, lex_addr)
    elif isinstance(e, TNat):
        return isinstance(e2, TNat)
    elif isinstance(e, TInt):
        return isinstance(e2, TInt)
    elif isinstance(e, TRational):
        return isinstance(e2, TRational)
    elif isinstance(e, TString):
        return isinstance(e2, TString)
    elif isinstance(e, TBoolean):
        return isinstance(e2, TBoolean)
    elif isinstance(e, TEither):
        return isinstance(e2, TEither) and \
            alpha_equiv(e.left, e2.left, lex_env, lex_addr) and \
            alpha_equiv(e.right, e2.right, lex_env, lex_addr)

    elif isinstance(e, TList):
        return isinstance(e2, TList) and \
            alpha_equiv(e.contents, e2.contents, lex_env, lex_addr)
    elif isinstance(e, TMaybe):
        return isinstance(e2, TMaybe) and \
            alpha_equiv(e.subtype, e2.subtype, lex_env, lex_addr)
    elif isinstance(e, TFunction):
        return isinstance(e2, TFunction) and \
            alpha_equiv(e.input, e2.input, lex_env, lex_addr) and \
            alpha_equiv(e.output, e2.output, lex_env, lex_addr)
    elif isinstance(e, TEqual):
        raise NotImplementedError
    elif isinstance(e, TForAll):
        if not isinstance(e2, TForAll):
            return False
        else:
            return alpha_equiv(e.var, e2.var, lex_env, lex_addr) and \
                alpha_equiv(e.prop, e2.prop, lex_env, lex_addr)
    elif isinstance(e, TExists):
        raise NotImplementedError
    elif isinstance(e, TAbsurd):
        raise NotImplementedError

    else:
        raise Exception(f"Unsupported expression in alpha: {e}")


def is_numeric_subtype(τ1 : Type, τ2 : type) -> bool:
    if isinstance(τ1, TNat):
        return (isinstance(τ2, TNat) or isinstance(τ2, TInt) or isinstance(τ2, TRational))
    if isinstance(τ1, TInt):
        return isinstance(τ2, TInt) or isinstance(τ2, TRational)
    else:
        return False
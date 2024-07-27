from ..defs import *
from .equiv import alpha_equiv, is_numeric_subtype
from fractions import Fraction
from traceback import format_exc
from loguru import logger


"""
Class to implement Normalization by Evaluations:

Expressions Handled by Synth:
   Variable, Literal, 
   Application
   PrintThen
   If
   Plus, Times
   Or, And, Not, Equal
   Concat, Contains, 
   Append, Empty, Car, Cdr, Length
   Let

Expressions Handled by Check:
   Lambda
   List
   Just
   ENothing
   Refl, Symm, Trans, Cong
   Look

"""

class NbEError(Exception):
    pass

class Normalizer():
    def __init__(self):
        pass

    def is_numeric_type(self, τ):
        return (isinstance(τ, TNat) or isinstance(τ, TInt) or isinstance(τ, TRational))

    def eval(self, e : Expr) -> Expr:
        Γ = Context()
        return self.synth(Γ, e)

    ###############
    ## Synth Helpers
    ###############

    
    def synth_literal(self, l : Literal) -> Expr:
        t = l.type
        v = l.val
        l.normalized = True
        l.typed = True
        if (isinstance(v, str)):
            res = Literal(v, TString())
        elif (isinstance(v, bool)):
            res = Literal(v, TBoolean())
        elif (isinstance(v, int) and (v >= 0)):
            res = Literal(v, TNat())
        elif isinstance(v, int):
            res = Literal(v, TInt())
        elif isinstance(v, Fraction):
            res = Literal(v, TRational())
            raise NotImplementedError
        elif isinstance(v, float):
            raise NotImplementedError
        else:
            raise NbEError(f"Found Invalid literal/type combo at {v} : {t}")
        res.normalized = True
        res.typed = True
        return res
    
    def synth_print(self, Γ : Context, e : PrintThen) -> PrintThen:
        e = self.synth(Γ, e)
        res = PrintThen(e.type, e)
        res.normalized = True
        res.typed = True
        return res
    
    def synth_app(self, Γ : Context, e : Application) -> Expr:
        if not isinstance(e.operator, Lambda):
            op = self.synth(Γ, e.operator)
        else:
            op = e.operator
        #logger.info(Γ)
        logger.info(e.operator)
        # op = self.synth(Γ, e.operator)
        logger.info(op.type)
        if isinstance(op.type.input, Variable):
            arg = self.check(Γ, e.operand, op.type.input.type)
            input_ty = op.type.input.type
        else:
            arg = self.check(Γ, e.operand, op.type.input)
            input_ty = op.type.input
        logger.info(arg)
        #logger.info(f'{op}, {op.type}')
        #logger.info(f'{arg}, {arg.type}')
        if not (isinstance(op.type, TFunction) or isinstance(op.type, TForAll)):
            raise NbEError(f"Invalid Function type for {op}, {op.type}")
        

        arg_ty = arg.type
        # logger.debug(input_ty)
        if not (alpha_equiv(input_ty, arg_ty)):

            raise NbEError(f"Invalid Argument type when expecting {input_ty}: {arg_ty} for {arg}")
        if isinstance(op, Lambda):
            Γ2 = Γ.copy()
            Γ2.extend(op.var, arg)
            return self.check(Γ2, op.body, op.body.type)
        else:
            res = Application(op, arg)
            if isinstance(op.type, TFunction):
                res.type = op.type.output
            elif isinstance(op.type, TForAll):
                res.type = op.type.prop
            else:
                new_ty = Let(Variable("_f", TFunction(arg.type, op.type)),
                             Lambda(Variable("_a", arg.type)))
                res_type = self.synth()
            res.normalized = True
            res.typed = True
        return res
        
    def synth_if(self, Γ : Context, e : If) -> Expr:
        test = self.synth(Γ, e.test)
        if not isinstance(test.type, TBoolean):
            raise NbEError(f"Non-Boolean type when at top of if {test}: {test.type}")
        conseq = self.synth(Γ, e.consequent)
        els    = self.synth(Γ, e.else_expr)
        if not alpha_equiv(conseq.type, els.type):
            raise NbEError(f"Non-Equiv types for cases of if: {conseq.type}: {els.type}")
        elif isinstance(test, Literal):
            if test.val:
                return conseq
            else:
                return els
        else:
            res = If(test, conseq, els, conseq.type)
            res.normalized = True
            res.typed = True
            return res


    def synth_plus(self, Γ : Context, e : Plus) -> Expr:
        e1 = self.synth(Γ, e.e1)
        e2 = self.synth(Γ, e.e2)
        if not self.is_numeric_type(e1.type):
            raise NbEError(f"Non-numeric type in Plus e1: {e1.type}")
        if not self.is_numeric_type(e2.type):
            raise NbEError(f"Non-numeric type in Plus e2: {e2.type}")
        
        if isinstance(e1, Literal) and isinstance(e2, Literal):
            out_ty = merge_numeric_types(e1.type, e2.type)
            out_v = e1.val + e2.val
            res = Literal(out_v, out_ty)
        else:
            res = Plus(e1, e2)
        res.normalized = True
        res.typed = True
        return res
    
    def synth_times(self, Γ : Context, e : Times) -> Expr:
        e1 = self.synth(Γ, e.e1)
        e2 = self.synth(Γ, e.e2)
        if not self.is_numeric_type(e1.type):
            raise NbEError(f"Non-numeric type in Times e1: {e1.type}")
        if not self.is_numeric_type(e2.type):
            raise NbEError(f"Non-numeric type in Times e2: {e2.type}")
        
        if isinstance(e1, Literal) and isinstance(e2, Literal):
            out_ty = merge_numeric_types(e1.type, e2.type)
            out_v = e1.val * e2.val
            res = Literal(out_v, out_ty)
        else:
            res = Times(e1, e2)
        res.normalized = True
        res.typed = True
        return res
    
    def synth_or(self, Γ : Context, e : Or) -> Expr:
        e1 = self.synth(Γ, e.e1)
        e2 = self.synth(Γ, e.e2)
        if not isinstance(e1.type, TBoolean):
            raise NbEError(f"Non-boolean type in Or e1: {e1.type}")
        if not isinstance(e1.type, TBoolean):
            raise NbEError(f"Non-boolean type in Or e2: {e2.type}")
        if isinstance(e1, Literal) and isinstance(e2, Literal):
            out_v = e1.val or e2.val
            res = Literal(out_v, TBoolean())
        else:
            res = Or(e1, e2)
        res.normalized = True
        res.typed = True
        return res
    
    def synth_and(self, Γ : Context, e : And) -> Expr:
        e1 = self.synth(Γ, e.e1)
        e2 = self.synth(Γ, e.e2)
        if not isinstance(e1.type, TBoolean):
            raise NbEError(f"Non-boolean type in And e1: {e1.type}")
        if not isinstance(e1.type, TBoolean):
            raise NbEError(f"Non-boolean type in And e2: {e2.type}")
        if isinstance(e1, Literal) and isinstance(e2, Literal):
            out_v = e1.val and e2.val
            res = Literal(out_v, TBoolean())
        else:
            res = And(e1, e2)
        res.normalized = True
        res.typed = True
        return res
    
    def synth_not(self, Γ : Context, e : Not) -> Expr:
        e1 = self.synth(Γ, e.e1)
        if not isinstance(e1.type, TBoolean):
            raise NbEError(f"Non-boolean type in Not: {e1.type}")
        if isinstance(e1, Literal):
            out_v = not e1.val
            res = Literal(out_v, TBoolean())
        else:
            res = Not(e1)
        res.normalized = True
        res.typed = True
        return res

    ## equality only normalizes when both inputs are literals
    def synth_eq(self, Γ : Context, e : Equal) -> Expr:
        e1 = self.synth(Γ, e.e1)
        e2 = self.synth(Γ, e.e2)
        if isinstance(e1, Literal) and isinstance(e2, Literal):
            out_v = e1.val == e2.val
            res = Literal(out_v, TBoolean())
        else:
            res = Equal(e1, e2)
        res.normalized = True
        res.typed = True
        return res
        
    def synth_concat(self, Γ : Context, e : Concat) -> Expr:
        s1 = self.synth(Γ, e.e1)
        s2 = self.synth(Γ, e.e2)
        if not isinstance(s1.type, TString):
            raise NbEError(f"Non-string type in Concat e1: {s1.type}")
        if not isinstance(s1.type, TString):
            raise NbEError(f"Non-string type in Concat e2: {s2.type}")
        if isinstance(s1, Literal) and isinstance(s2, Literal):
            out_v = s1.val + s2.val
            res = Literal(out_v, TString())
        else:
            res = Concat(s1, s2)
        res.normalized = True
        res.typed = True
        return res
    
    def synth_contains(self, Γ : Context, e : Contains) -> Expr:
        s1 = self.synth(Γ, e.e1)
        s2 = self.synth(Γ, e.e2)
        if not isinstance(s1.type, TString):
            raise NbEError(f"Non-string type in Contains e1: {s1.type}")
        if not isinstance(s1.type, TString):
            raise NbEError(f"Non-string type in Contains e2: {s2.type}")
        if isinstance(s1, Literal) and isinstance(s2, Literal):
            out_v = s1.val + s2.val
            res = Literal(out_v, TString())
        else:
            res = Contains(s1, s2)
        res.normalized = True
        res.typed = True
        return res
    
    def synth_append(self, Γ : Context, e : Append) -> Expr:
        s1 = self.synth(Γ, e.e1)
        s2 = self.synth(Γ, e.e2)
        if not isinstance(s1.type, TList):
            raise NbEError(f"Non-list type in Append e1: {s1.type}")
        if not isinstance(s1.type, TList):
            raise NbEError(f"Non-list type in Append e2: {s2.type}")
        if not alpha_equiv(s1.type, s2.type):
            raise NbEError(f"Non-equiv list types in Append e2: {s1.type}, {s2.type}")
        if isinstance(s1, Literal) and isinstance(s2, Literal):
            out_v = s1.val + s2.val
            res = List(out_v, s1.type)
        else:
            res = Append(s1, s2, s1.type)
        res.normalized = True
        res.typed = True
        return res
    
    def synth_empty(self, Γ : Context, e : Empty) -> Expr:
        l = self.synth(Γ, e.e1)
        if not isinstance(l.type, TList):
            raise NbEError(f"Non-list type in Empty e1: {l.type}")
        if isinstance(l, List):
            out_v = len(l.values) == 0
            res = Literal(out_v, TBoolean())
        else:
            res = Empty(l)
        res.normalized = True
        res.typed = True
        return res
    
    def synth_length(self, Γ : Context, e : Length) -> Expr:
        l = self.synth(Γ, e.e1)
        if not isinstance(l.type, TList):
            raise NbEError(f"Non-list type in Empty e1: {l.type}")
        if isinstance(l, List):
            out_v = len(l.values)
            res = Literal(out_v, TNat())
        else:
            res = Length(l)
        res.normalized = True
        res.typed = True
        return res
    
    ## only evaluates if value and all list elements are literals
    def synth_member(self, Γ : Context, e : Member) -> Expr:
        x = self.synth(Γ, e.value)
        l = self.synth(Γ, e.list)
        if not isinstance(l.type, TList):
            raise NbEError(f"Non-list type in Empty e1: {l.type}")
        if isinstance(x, Literal) and isinstance(l, List):
            all_literals = all([isinstance(e, Literal) for e in l.values])
            if all_literals:
                res = Literal(False, TBoolean())
                for v in l.values:
                    if isinstance(v, Literal):
                        if x.val == v.val:
                            res = Literal(True, TBoolean())
                res.normalized = True
                res.typed = True
                return res
        res = Member(x, l)
        res.normalized = True
        res.typed = True
        return res
    
    def synth_let(self, Γ : Context, e : Let) -> Expr:
        #logger.debug(f"Let Expr: {e}")
        x : Variable = e.var
        a = self.check(Γ, e.bind, x.type)
        #logger.info(e.bind)
        Γ2 = Γ.copy()
        Γ2.extend(x, a)
        return self.synth(Γ2, e.body)
    
    def synth_induct_nat(self, Γ : Context, arg : Expr, out_type : Expr, inds : Expr, base : Expr, inst_type : Expr):
        base_type = self.synth(Application(out_type, Literal(0)))
        base = self.check(Γ, base, base_type)
        new_var = Variable("_n", TNat())
        Γ2 = Γ.copy()
        Γ2.extend(new_var, new_var)
        rec_type = self.synth(Γ2, Application(out_type, new_var)) 
        ind_step = self.synth(Γ2, Application(out_type, Plus(Literal(1, TNat()), new_var))) 
        ind_type = TForAll(new_var, TForAll(Variable("_IH", rec_type), ind_step))
        ind = self.check(Γ, inds[0], ind_type)
        def synth_induct_nat_helper(e : Expr):
            if isinstance(e, Literal):
                if (e.val == 0):
                    return base
                else:
                    v = synth_induct_nat_helper(Literal(e.val - 1, TNat()))
                    return self.synth(Γ, Application(Application(ind, e.val - 1), v))
            elif isinstance(e, Plus):
                if isinstance(e.e1, Literal) and isinstance(e.e1.type, TNat):
                    if e.e1.val == 0:
                        raise NbEError(f"Found 0 at top of normalized plus: {e}")
                    elif e.e1.val < 0:
                        raise NbEError(f"Found negative in TNat Literal")
                    else:
                        v = synth_induct_nat_helper(Plus(Literal(e.e1.val - 1, TNat), e.e2))
                        return self.synth(Γ, Application(Application(ind, e.e1.val - 1), v))
                else:
                    res = Induct(e, out_type, base, [ind], inst_type)
                    res.normalized = True
                    res.typed = True
                    return res
                
        return synth_induct_nat_helper(arg)

    def synth_induct_int(self, Γ : Context, arg : Expr, out_type : Expr, inds : Expr, base : Expr, inst_type : Expr):
        base_type = self.synth(Application(out_type, Literal(0)))
        base = self.check(Γ, base, base_type)
        new_var = Variable("_i", TInt())
        Γ2 = Γ.copy()
        Γ2.extend(new_var, new_var)
        rec_type = self.synth(Γ2, Application(out_type, new_var)) 
        ind_pos_step = self.synth(Γ2, Application(out_type, Plus(Literal(1, TNat()), new_var))) 
        ind_neg_step = self.synth(Γ2, Application(out_type, Plus(Literal(-1, TInt()), new_var))) 
        ind_type_pos = TForAll(new_var, TForAll(Variable("_IH", rec_type), ind_pos_step))
        ind_type_neg = TForAll(new_var, TForAll(Variable("_IH", rec_type), ind_neg_step))
        ind_pos = self.check(Γ, inds[0], ind_type_pos)
        ind_neg = self.check(Γ, inds[1], ind_type_neg)
        def synth_induct_int_helper(e : Expr):
            if isinstance(e, Literal):
                if (e.val == 0):
                    return base
                elif (e.val < 0):
                    v = synth_induct_int_helper(Literal(e.val + 1, TInt()))
                    return self.synth(Γ, Application(ind_neg, v))
                else:
                    v = synth_induct_int_helper(Literal(e.val - 1, TNat()))
                    return self.synth(Γ, Application(ind_pos, v))
            elif isinstance(e, Plus):
                if isinstance(e.e1, Literal) and isinstance(e.e1.type, TNat):
                    if e.e1.val == 0:
                        raise NbEError(f"Found 0 at top of normalized plus: {e}")
                    elif e.e1.val < 0:
                        v = synth_induct_int_helper(Plus(Literal(e.e1.val + 1, TInt()), e.e2))
                        return self.synth(Γ, Application(ind_neg, v))
                    else:
                        v = synth_induct_int_helper(Plus(Literal(e.e1.val - 1, TNat()), e.e2))
                        return self.synth(Γ, Application(ind_pos, v))
                else:
                    res = Induct(e, out_type, base, [ind_pos, ind_neg], inst_type)
                    res.normalized = True
                    res.typed = True
                    return res
        return synth_induct_int_helper(arg)
    
    def synth_induct_maybe(self, Γ : Context, arg : Expr, out_type : Expr, inds : Expr, base : Expr, inst_type : Expr):
        base_type = self.synth(Application(out_type, Literal(0)))
        base = self.check(Γ, base, base_type)
        new_var = Variable("_maybe", arg.type)
        Γ2 = Γ.copy()
        Γ2.extend(new_var, new_var)
        rec_type = self.synth(Γ2, Application(out_type, new_var)) 
        ind_pos_step = self.synth(Γ2, Application(out_type, Plus(Literal(1, TNat()), new_var)))
        ind_type_pos = TForAll(Variable("_IH", rec_type), ind_pos_step)
        ind = self.check(Γ, inds[0], ind_type_pos)
        def synth_induct_maybe_helper(e : Expr):
            if isinstance(e, ENothing):
                return base
            elif isinstance(e, Just):
                return self.check(Γ, Application(ind, e.e1), rec_type, inst_type)
            else:
                res = Induct(e, out_type, base, [ind], inst_type)
                res.normalized = True
                res.typed = True
                return res
        return synth_induct_maybe_helper(arg)
    
    def synth_induct_list(self, Γ : Context, arg : Expr, out_type : Expr, inds : Expr, base : Expr, inst_type : Expr):
        base_type = self.synth(Γ, Application(out_type, Literal(0, TNat())))
        base = self.check(Γ, base, base_type)
        new_var = Variable("_elem", arg.type.type)
        ls      = Variable("_ls", arg.type)
        Γ2 = Γ.copy()
        Γ2.extend(new_var, new_var)
        Γ2.extend(ls, ls)
        rec_type = self.synth(Γ2, Application(out_type, new_var)) 
        ind_step = self.synth(Γ2, Application(out_type, Plus(Literal(1, TNat()), new_var))) 
        ind_type = TForAll(new_var, TForAll(Variable("_IH", rec_type), ind_step))
        ind = self.check(Γ, inds[0], ind_type)
        def synth_induct_list_helper(e : Expr):
            if isinstance(e, List):
                if len(e.values) == 0:
                    return base
                else:
                    new_ls = List(e.values[1:].copy(), e.type)
                    v = synth_induct_list_helper(new_ls)
                    return self.synth(Γ, Application(Application(ind, e.values[0]), v))
            elif isinstance(e, Append):
                if isinstance(e.e1, List):
                    if len(e.e1.values) == 0:
                        raise NbEError(f"Found empty list at top of normalized append: {e}")
                    else:
                        new_ls = List(e.e1.values[1:].copy(), e.e1.type)
                        v = synth_induct_list_helper(Append(new_ls, e.e2))
                        return self.synth(Γ, Application(Application(ind, e.e1.values[0]), v))
                else:
                    res = Induct(e, out_type, base, [ind], inst_type)
                    res.normalized = True
                    res.typed = True
                    return res
                
        return synth_induct_list_helper(arg)
    
    def synth_induct_either(self, Γ : Context, arg : Expr, out_type : Expr, inds : Expr, base : Expr, inst_type : Expr):
        raise NotImplementedError
    
    def synth_induct_eq(self, Γ : Context, arg : Expr, out_type : Expr, inds : Expr, base : Expr, inst_type : Expr):
        raise NotImplementedError

    def synth_induct(self, Γ : Context, e : Induct) -> Expr:
        arg = self.synth(Γ, e.arg)
        out_type = self.synth(Γ, e.out_type)
        if not isinstance(out_type, Lambda):
            raise NbEError(f"Not a Lambda: {out_type}")
        if not alpha_equiv(arg.type, out_type.var.type):
            raise NbEError(f"Invalid type function input type for {arg.type} : {out_type.var.type}")
        
        inst_type = self.synth(Γ, Application(out_type, arg))
        if isinstance(arg.type, TNat):
            return self.synth_induct_nat(Γ, arg, out_type, e.inds, e.base, inst_type)
        if isinstance(arg.type, TInt):
            return self.synth_induct_int(Γ, arg, out_type, e.inds, e.base, inst_type)
        if isinstance(arg.type, TMaybe):
            return self.synth_induct_maybe(Γ, arg, out_type, e.inds, e.base, inst_type)
        if isinstance(arg.type, TList):
            return self.synth_induct_list(Γ, arg, out_type, e.inds, e.base, inst_type)
        if isinstance(arg.type, TEither):
            return self.synth_induct_either(Γ, arg, out_type, e.inds, e.base, inst_type)
        if isinstance(arg.type, TEqual):
            return self.synth_induct_eq(Γ, arg, out_type, e.inds, e.base, inst_type)
        else:
            raise NbEError(f"Induct expected an Inductive Type, got {arg.type}")

    def synth(self, Γ : Context, e : Expr) -> Expr:
        res = None

        ## base cases
        if isinstance(e, Variable):
            res = Γ.lookup(e.name)
        elif isinstance(e, Literal):
            res = self.synth_literal(e)

        ## Sample
        elif isinstance(e, PrintThen):
            print(e.message)
            res = self.synth_print(Γ, e.body)
        
        ## Numbers
        elif isinstance(e, Plus):
            res = self.synth_plus(Γ, e)
        elif isinstance(e, Times):
            res = self.synth_times(Γ, e)

        ## Booleans
        elif isinstance(e, If):
            res = self.synth_if(Γ, e)
        elif isinstance(e, Or):
            res = self.synth_or(Γ, e)
        elif isinstance(e, And):
            res = self.synth_and(Γ, e)
        elif isinstance(e, Not):
            res = self.synth_not(Γ, e)
        elif isinstance(e, Equal):
            res = self.synth_eq(Γ, e)

        ## Strings
        elif isinstance(e, Concat):
            res = self.synth_concat(Γ, e)
        elif isinstance(e, Contains):
            res = self.synth_contains(Γ, e)

        ## Lists
        elif isinstance(e, Append):
            res = self.synth_append(Γ, e)
        elif isinstance(e, Empty):
            res = self.synth_empty(Γ, e)
        elif isinstance(e, Member):
            res = self.synth_member(Γ, e)
        elif isinstance(e, Length):
            res = self.synth_length(Γ, e)

        ## Environment Mutation
        elif isinstance(e, Let):
            res = self.synth_let(Γ, e)
        elif isinstance(e, Application):
            res = self.synth_app(Γ, e)

        ## dependent types
        elif isinstance(e, Induct):
            res = self.synth_induct(Γ, e)

        ## Type expressions
        elif isinstance(e, TUniverse):
            level = self.synth(Γ, e.level)
            if not isinstance(level.type, TNat):
                raise NbEError(f"Expected universe level to have nat type, got: {level}")
            level = self.check(Γ, Plus(Literal(1, TNat()), level), TNat())
            level2 = self.check(Γ, Plus(Literal(2, TNat()), level), TNat())
            res = TUniverse(level)
            res.type = TUniverse(level2)
            res.normalized = True
            res.typed = True
        elif isinstance(e, TNat):
            res = TNat()
            res.type = TUniverse(Literal(0, TNat()))
            res.normalized = True
            res.typed = True
        elif isinstance(e, TInt):
            res = TInt()
            res.type = TUniverse(Literal(0, TNat()))
            res.normalized = True
            res.typed = True
        elif isinstance(e, TRational):
            res = TRational()
            res.type = TUniverse(Literal(0, TNat()))
            res.normalized = True
            res.typed = True
        elif isinstance(e, TString):
            res = TString()  
            res.type = TUniverse(Literal(0, TNat()))
            res.normalized = True
            res.typed = True
        elif isinstance(e, TBoolean):
            res = TBoolean()  
            res.type = TUniverse(Literal(0, TNat()))
            res.normalized = True
            res.typed = True
        elif isinstance(e, TEither):
            lft = self.synth(Γ, e.left)
            rght = self.synth(Γ, e.right)
            if not (isinstance(lft.type, TUniverse) and isinstance(rght.type, TUniverse)):
                raise NbEError(f"Expected either subtypes type to be universe, got: {lft.type}, {rght.type}")
            level = self.check(Γ, Plus(Literal(1, TNat()), Max(lft.type.level, rght.type.level)), TNat())
            res_ty = TUniverse(level)
            res_ty.normalized = True
            res_ty.typed = True
            res = TEither(lft.type, rght.type, res_ty)
            res.normalized = True
            res.typed = True

        elif isinstance(e, TList):
            elem_ty = self.synth(Γ, e.contents)
            if isinstance(elem_ty, TUniverse):
                level = self.check(Γ, Plus(Literal(1, TNat()), elem_ty.level), TNat())
                res_ty = TUniverse(elem_ty.level+1)
            else:
                res_ty = TUniverse(Literal(0, TNat()))
            res_ty.normalized = True
            res_ty.typed = True
            res = TList(elem_ty, res_ty)
            res.normalized = True
            res.typed = True
        elif isinstance(e, TMaybe):
            subty = self.synth(Γ, e.subtype)
            if not isinstance(subty, TUniverse):
                raise NbEError(f"Expected maybe subtype type to be universe, got: {subty}")
            level = self.check(Γ, Plus(Literal(1, TNat()), subty.level), TNat())
            res_ty = TUniverse(level)
            res = TList(elem_ty, res_ty)
            res.normalized = True
            res.typed = True
        elif isinstance(e, TFunction):
            Γ2 = Γ.copy()
            Γ2.extend(e.input, e.input)
            body = self.synth(Γ2, e.output)
            res = TFunction(e.input, body)
            if not isinstance(body.type, TUniverse):
                raise NbEError(f"Expected function output type type to be universe, got: {body.type}")
            level = self.check(Γ, Plus(Literal(1, TNat()), body.type.level), TNat())
            res.type = TUniverse(level)
            res.normalized = True
            res.typed = True
        elif isinstance(e, TEqual):
            raise NotImplementedError
        elif isinstance(e, TForAll):
            raise NotImplementedError
        elif isinstance(e, TExists):
            raise NotImplementedError
        elif isinstance(e, TAbsurd):
            raise NotImplementedError
        else:
            raise NbEError(f"Unknown Expression in synth: {e}")
        assert isinstance(res, Expr)
        assert res.normalized and res.typed
        return res

    ###############
    ## Check Helpers
    ###############

    def check_lambda(self, Γ : Context, e : Lambda, τ : Type) -> Expr:
        if not (isinstance(τ, TFunction) or isinstance(τ, TForAll)):
            logger.error(e)
            logger.error(τ)
            logger.error(Γ)
            raise NbEError(f"Expected function type for Lambda {e}, got: {τ}")
        x = e.var
        Γ2 = Γ.copy()
        Γ2.extend(x, x)
        if isinstance(τ, TFunction):
            b : Expr = self.check(Γ2, e.body, τ.output)
        elif isinstance(τ, TForAll):
            b : Expr = self.check(Γ2, e.body, τ.output)
        else:
            raise NbEError(f"Invalid function type: {τ}")
        res = Lambda([x], b)
        res.type = τ
        res.normalized = True
        res.typed = True
        logger.info(res)
        return res
    
    def check_list(self, Γ, e : List, τ : Type) -> Expr:
        if not isinstance(τ, TList):
            raise NbEError(f"Expected list type for List, got: {τ}")
        ty_elems = τ.contents
        vs = [self.check(Γ, elem, ty_elems) for elem in e.values]
        res = List(vs, TList(ty_elems))
        res.normalized = True
        res.typed = True
        return res

    def check_left(self, Γ, e : Left, τ : Type) -> Expr:
        if not isinstance(τ, TEither):
            raise NbEError(f"Expected Eiither type for Left, got: {τ}")
        ty = τ.left
        r = self.check(Γ, e.e1, ty)
        res = Left(r, τ)
        res.normalized = True
        res.typed = True
        return res

    def check_right(self, Γ, e : Right, τ : Type) -> Expr:
        if not isinstance(τ, TEither):
            raise NbEError(f"Expected Either type for Right, got: {τ}")
        ty = τ.right
        r = self.check(Γ, e.e1, ty)
        res = Right(r, τ)
        res.normalized = True
        res.typed = True

    ## Maybe Expressions
    def check_nothing(self, Γ, e : ENothing, τ : Type) -> Expr:
        if not isinstance(τ, TMaybe):
            raise NbEError(f"Expected Maybe type for nothing, got: {τ}")
    
        res = ENothing(τ)
        res.normalized = True
        res.typed = True

    def check_just(self, Γ, e : Just, τ : Type) -> Expr:
        body = e.e1
        if not isinstance(τ, TMaybe):
            raise NbEError(f"Expected Maybe type for just, got: {τ}")
    
        else:
            e = self.check(Γ, body, τ.type)
            res = Just(e, TMaybe(e.type))
            res.normalized = True
            res.typed = True
            
    ## = Expressions
    def check_refl(self, Γ, e : Refl, τ : Type) -> Expr:
        if not isinstance(τ, TEqual):
            raise NbEError(f"Expected Equal type for refl, got: {τ}")
        elif not alpha_equiv(τ.lhs, τ.rhs):
            raise NbEError(f"Cannot use refl to make Equal expressions that is not same, got: {τ}")
        ex = self.check(Γ, e.val, τ.type)
        if not alpha_equiv(τ.lhs, ex):
            raise NbEError(f"Invalid type for {ex}: {τ}")
        else:
            res = Refl(ex, TEqual(ex.type, ex, ex))
            res.normalized = True
            res.typed = True
            return res
        
    def check_symm(self, Γ, e : Symm, τ : Type) -> Expr:
        if not isinstance(τ, TEqual):
            raise NbEError(f"Expected Equal type for symm, got: {τ}")
        e = self.check(Γ, e.body, TEqual(τ.type, τ.rhs, τ.lhs))
        res = Symm(e, τ)
        res.normalized = True
        res.typed = True
        return res

    def check_trans(self, Γ, e : Trans, τ : Type) -> Expr:
        if not isinstance(τ, TEqual):
            raise NbEError(f"Expected Equal type for trans, got: {τ}")
        e1 = self.synth(Γ, e.e1)
        e2 = self.synth(Γ, e.e2)
        if not isinstance(e1.type, TEqual):
            raise NbEError(f"Expected Equal type for trans arg 1, got: {e1.type}")
        if not isinstance(e2.type, TEqual):
            raise NbEError(f"Expected Equal type for trans arg 2, got: {e2.type}")
        if not alpha_equiv(e1.type.rhs, e2.type.lhs):
            raise NbEError(f"Invalid middle terms for trans: {e1.type.rhs}, {e2.type.lhs}")
        res_ty = TEqual(e1.type.type, e1.type.lhs, e2.type.rhs)
        if not alpha_equiv(res_ty, τ):
            raise NbEError(f"Invalid final type terms for trans: Expected {τ}, got {res_ty}")
        res = Trans(e1, e2, res_ty)
        res.normalized = True
        res.typed = True
        
    
    def check_cong(self, Γ, e : Cong, τ : Type) -> Expr:
        if not isinstance(τ, TEqual):
            raise NbEError(f"Expected Equal type for cong, got: {τ}")
        op = self.synth(Γ, e.fn)
        exp = self.synth(Γ, e.e1)
        if not isinstance(op.type, TForAll):
            raise NbEError(f"Expected ForAll type for cong fn, got: {op.type}")
        if not isinstance(exp.type, TEqual):
            raise NbEError(f"Expected Equal type for cong exp, got: {exp.type}")
        e1 = exp.type.lhs
        e2 = exp.type.rhs
        f_e1 = self.check(Γ, Application(op, e1), τ.type)
        f_e2 = self.check(Γ, Application(op, e2), τ.type)
        res_ty = TEqual(τ.type, f_e1, f_e2)
        res = Cong(op, exp, res_ty)
        res.normalized = True
        res.typed = True
        return res
        
    ## Σ Expressions
    def check_look(self, Γ, e : Look, τ : Type) -> Expr:
        if not isinstance(τ, TExists):
            raise NbEError(f"Expected Exists type for look exp, got: {τ}")
        a = e.element
        d = e.proof
        a = self.check(Γ, a, τ.var_type)
        raise NotImplementedError
    
    def check_car(self, Γ, e : Car, τ : Type) -> Expr:
        e = self.synth(Γ, e.e1)
        if not isinstance(e.type, TExists):
            raise NbEError(f"Expected Exists type for car argument, got: {τ}")
        if not alpha_equiv(τ, e.type.var_type):
            raise NbEError(f"Mismatched types between car pair car and expectation, got {e.type.var_type} but expected {τ}")
        elif isinstance(e, Look):
            return e.element
        else:
            res = Car(e)
            res.type = e.type.var_type
            res.normalized = True
            res.typed = True
            return res
        

    def check_cdr(self, Γ, e : Cdr, τ : Type) -> Expr:
        raise NotImplementedError

    def check(self, Γ : Context, e: Expr, τ : Type) -> Expr:
        res = None
        logger.debug(f"in check with {e}, {τ}")
        # if 'Type' in str(type(τ)):
        #     raise ValueError(f'cannot check Type for: {e}')
        if isinstance(e, Lambda):
            res = self.check_lambda(Γ, e, τ)
        elif isinstance(e, List):
            res = self.check_list(Γ, e, τ)
        elif isinstance(e, ENothing):
            res = self.check_nothing(Γ, e, τ)
        elif isinstance(e, Just):
            res = self.check_just(Γ, e, τ)
        elif isinstance(e, Refl):
            res = self.check_refl(Γ, e, τ)
        elif isinstance(e, Symm):
            res = self.check_symm(Γ, e, τ)
        elif isinstance(e, Trans):
            res = self.check_trans(Γ, e, τ)
        elif isinstance(e, Cong):
            res = self.check_cong(Γ, e, τ)
        elif isinstance(e, Look):
            res = self.check_look(Γ, e, τ)
        elif isinstance(e, Left):
            res = self.check_left(Γ, e, τ)
        elif isinstance(e, Right):
            res = self.check_right(Γ, e, τ)

        else:
            e2 = self.synth(Γ, e)
            logger.debug(e2)
            logger.debug(e2.type)
            logger.debug(τ)
            α = alpha_equiv(e2.type, τ)
            if 'Type' in str(τ) and ('Type' not in str(e2.type)):
                res = e2
            elif α or is_numeric_subtype(e2.type, τ):
                e2.type = τ
                res = e2
            else:
                raise NbEError(f"Encounted invalid type from synth case of check when expecting {τ}: {e2.type}")
        try:
            assert isinstance(res, Expr)
            assert res.normalized and res.typed
            return res
        except Exception as err:
            logger.error(format_exc())
            logger.error(f"Error for exp type {type(res)}: {res}")
            logger.info(f"normalized: {res.normalized}, typed: {res.typed}")
            raise err

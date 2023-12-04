from defs import *
from equiv import alpha_equiv, is_numeric_subtype


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


    ###############
    ## Synth Helpers
    ###############

    def synth_literal(l : Literal) -> Expr:
        t = l.type
        v = l.val
        l.normalized = True
        l.typed = True
        if isinstance(t, TNat):
            if (isinstance(v, int) and (v >= 0)):
                return l
        elif isinstance(t, TInt):
            if isinstance(v, int):
                return l
        elif isinstance(t, TRational):
            if (isinstance(v, int) or isinstance(v, float)):
                return l
        if isinstance(t, TString):
            if isinstance(v, str):
                return l
        if isinstance(t, TBoolean):
            if isinstance(v, bool):
                return l
        else:
            raise NbEError(f"Found Invalid literal/type combo at {v} : {t}")

    def synth_print(self, Γ : Context, e : PrintThen) -> PrintThen:
        e = self.synth(Γ, e)
        res = PrintThen(e.type, e)
        res.normalized = True
        res.typed = True
        return res
    
    def synth_app(self, Γ : Context, e : Application) -> Expr:
        op = self.synth(Γ, e.operator)
        arg = self.synth(Γ, e.operand)
        if (not ((isinstance(op.type, TFunction)) or isinstance(op.type, TForAll))):
            raise NbEError(f"Invalid Function type for {op}, {op.type}")
        input_ty = op.type.input
        arg_ty = arg.type
        if not (alpha_equiv(input_ty, arg_ty)):
            raise NbEError(f"Invalid Argument type when expecting {input_ty}: {arg_ty}")
        if isinstance(op, Lambda):
            Γ2 = Γ.copy()
            Γ2.extend(op.var, arg)
            return self.synth(Γ2, op.body)
        else:
            res = Application(op, arg)
            res.type = op.type.output
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
        x : Variable = e.var
        a = self.check(Γ, e.bind, x.type)
        Γ2 = Γ.copy()
        Γ2 = Γ2.extend(x, a)
        return self.synth(Γ, e.body)

    def synth_list_loop(self, Γ : Context, e : ListLoop) -> Expr:
        raise NotImplementedError
    
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
        elif isinstance(e, ListLoop):
            res = self.synth_list_loop(Γ, e)
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
            raise NbEError(f"Expected function type for Lambda, got: {τ}")
        x = e.var
        Γ2 = Γ.copy()
        Γ2.extend(x, x)
        b : Expr = self.check(Γ2, e.body, τ.output)
        res = Lambda([x], b)
        res.type = TForAll(x, b.type)
        res.normalized = True
        res.typed = True
        return res
    
    def check_list(self, Γ, e : List, τ : Type) -> Expr:
        if not isinstance(τ, TList):
            raise NbEError(f"Expected list type for List, got: {τ}")
        ty_elems = τ.contents
        vs = [self.check(Γ, elem, ty_elems) for elem in e.values]
        res = List(vs, TList(ty_elems))
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
        raise NotImplementedError
    
    def check_car(self, Γ, e : Car, τ : Type) -> Expr:
        raise NotImplementedError
    
    def check_cdr(self, Γ, e : Cdr, τ : Type) -> Expr:
        raise NotImplementedError

    def check(self, Γ : Context, e: Expr, τ : Type) -> Expr:
        res = None
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
        else:
            e2 = self.synth(Γ, e)
            α = alpha_equiv(e2.type, τ)
            if α:
                e2.type = τ
                res = e2
            else:
                raise NbEError(f"Encounted invalid type from synth case of check when expecting {τ}: {e2.type}")
        assert isinstance(res, Expr)
        assert res.normalized and res.typed
        return res

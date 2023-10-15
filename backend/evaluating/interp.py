from defs import *

class Interpreter():
    def __init__(self):
        pass

    def apply_closure(self, rator : Closure, rand : Value):
        env : Environment = rator.env
        env.extend(rator.var, rator.var_type, rand)
        return self._eval(rator.body, env)

    def merge_numeric_types(self, t1, t2):
        if isinstance(t1, TNat) and isinstance(t2, TNat):
            return TNat()
        elif isinstance(t1, TRational) or isinstance(t2, TRational):
            return TRational()
        else:
            return TInt()

    def eval(self, e : Expr):
        v = self._eval(e, Environment())
        return v.value

    def _eval(self, e : Expr, env : Environment) -> Value:
        ## base cases
        if isinstance(e, Literal):
            if isinstance(e.type, TNum):
                return VNumber(e.val, e.type)
            elif isinstance(e.type, TList):
                return VList(e.val, e.type)
            elif isinstance(e.type, TString):
                return VString(e.val)
            elif isinstance(e.type, TBoolean):
                return VBoolean(e.val)
            
        if isinstance(e, ENothing):
            return VNothing(e.type)

        ## print statement
        if isinstance(e, PrintThen):
            print(e.message)
            return self._eval(e.body, env)

        ## Environment Extension
        if isinstance(e, Variable):
            return env.lookup(e.var)
        
        if isinstance(e, Let):
            v = self._eval(e.bind, env)
            env.extend(e.var, e.var_type, v)
            return self._eval(e.body, env)
        
        ## Functions 
        if isinstance(e, Lambda):
            return Closure(e.var, e.var_type, env.copy(), e.body)

        if isinstance(e, Application):
            oper = self._eval(e.operator, env)
            if not isinstance(oper, Closure):
                raise RuntimeError(f"Expected a closure, found: {oper}")
            operand = self._eval(e.operand, env)
            return self.apply_closure(oper, operand)

        ## Booleans
        if isinstance(e, Or):
            b1 = self._eval(e.e1, env)
            b2 = self._eval(e.e2, env)
            if not (isinstance(b1, VBoolean) and isinstance(b2, VBoolean)):
                raise RuntimeError(f"Expected booleans, got {b1}, {b2}")
            else:
                return VBoolean(b1.value or b2.value)
        if isinstance(e, And):
            b1 = self._eval(e.e1, env)
            b2 = self._eval(e.e2, env)
            if not (isinstance(b1, VBoolean) and isinstance(b2, VBoolean)):
                raise RuntimeError
            else:
                return VBoolean(b1.value and b2.value)
            
        if isinstance(e, Not):
            b1 = self._eval(e.e1, env)
            if not isinstance(b1, VBoolean):
                raise RuntimeError
            else:
                return VBoolean(not b1.value)
            
        if isinstance(e, If):
            for t, c in e.cases.items():
                b = self._eval(t, env)
                if not isinstance(b, VNothing()) and not (isinstance(b, VBoolean) and not b.value):
                    return self._eval(c, env)
            return self._eval(e.else_expr, env)
                    
        
        ## Numbers
        if isinstance(e, Plus):
            n1 = self._eval(e.e1, env)
            n2 = self._eval(e.e2, env)
            if not (isinstance(n1, VNumber) and isinstance(n2, VNumber)):
                raise RuntimeError(f"Expected numbers, got {n1}, {n2}")
            else:
                ty = self.merge_numeric_types(n1.type, n2.type)
                return VNumber(n1.value + n2.value, ty)
        if isinstance(e, Times):
            n1 = self._eval(e.e1, env)
            n2 = self._eval(e.e2, env)
            if not (isinstance(n1, VNumber) and isinstance(n2, VNumber)):
                raise RuntimeError(f"Expected numbers, got {n1}, {n2}")
            else:
                ty = self.merge_numeric_types(n1.type, n2.type)
                return VNumber(n1.value * n2.value, ty)
            
        if isinstance(e, Divide):
            n1 = self._eval(e.e1, env)
            n2 = self._eval(e.e2, env)
            if not (isinstance(n1, VNumber) and isinstance(n2, VNumber)):
                raise RuntimeError(f"Expected numbers, got {n1}, {n2}")
            if n2.value == 0:
                raise RuntimeError(f"Cannot divide by 0")
            else:
                return VNumber(n1.value / n2.value, TRational())
        
        if isinstance(e, Mod):
            n1 = self._eval(e.e1, env)
            n2 = self._eval(e.e2, env)
            if not (isinstance(n1, VNumber) and isinstance(n2, VNumber)):
                raise RuntimeError(f"Expected numbers, got {n1}, {n2}")
            else:
                ty = self.merge_numeric_types(n1.type, n2.type)
                return VNumber(n1.value / n2.value)

        ## Strings
        if isinstance(e, Concat):
            s1 = self._eval(e.e1, env)
            s2 = self._eval(e.e2, env)
            if not (isinstance(s1, VString) and isinstance(s2, VString)):
                raise RuntimeError
            else:
                return VString(s1.value + s2.value)
        if isinstance(e, Contains):
            s1 = self._eval(e.e1, env)
            s2 = self._eval(e.e2, env)
            if not (isinstance(s1, VString) and isinstance(s2, VString)):
                raise RuntimeError
            else:
                return VBoolean(s1.value in s2.value)
            

        ## Lists
        if isinstance(e, Append):
            l1 = self._eval(e.e1, env)
            l2 = self._eval(e.e2, env)
            if not (isinstance(l1, VList) and isinstance(s2, VList)):
                raise RuntimeError
            if not (l1.type == l2.type):
                raise RuntimeError
            else:
                return VList(l1.value + l2.value)
        if isinstance(e, IsNull):
            l1 = self._eval(e.e1, env)
            if not (isinstance(l1, VList)):
                raise RuntimeError
            else:
                return VBoolean(len(l1.value) == 0)
        if isinstance(e, Car):
            l1 = self._eval(e.e1, env)
            if not (isinstance(l1, VList)):
                raise RuntimeError
            else:
                return l1.value[0]
            
        if isinstance(e, Cdr):
            l1 = self._eval(e.e1, env)
            if not (isinstance(l1, VList)):
                raise RuntimeError
            else:
                return VList(l1.value[1:], l1.type)
            
        ## Maybe
        if isinstance(e, Just):
            v = self._eval(e, env)
            return VJust(e, v.type)
            
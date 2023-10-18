from loguru import logger
import sys
from ..defs import *

class Interpreter():
    def __init__(self):
        pass

    def apply_closure(self, rator : Closure, rand : Value):
        env : Environment = rator.env
        env.extend(rator.var, rand)
        logger.info(str(rator))
        return self._eval(rator.body, env)

    def init_env(self, es : list[Expr]) -> Environment:
        env = Environment()
        for e in es:
            if isinstance(e, Defconst):
                logger.info(f'extending {e.var} : {e.body.type} with {e.body}')
                env.extend(e.var, self._eval(e.body, env))
                logger.info(f"Env: {env.vars}")
            elif isinstance(e, Defunc):
                var : Variable = e.var
                env.extend(var, self._eval(e.body, env))
            elif isinstance(e, Defrel):
                raise NotImplementedError
            else:
                pass
            logger.info(f"Current Env: {env}")
        for x in env.vars:
            if isinstance(x[1], Closure):
                x[1].env = env.copy()
        logger.info(f"Final Env: {env}")
        return env

    def eval_file(self, es : list[Expr], ρ : Environment) -> list[Value]:
        ans = []
        for e in es:
            if not isinstance(e, Def):
                ans.append(self._eval(e, ρ))
        return ans


    def eval(self, e : Expr):
        v = self._eval(e, Environment())
        return v

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
            return env.lookup(e.name)
        
        if isinstance(e, Let):
            v = self._eval(e.bind, env)
            env.extend(e.var, v)
            return self._eval(e.body, env)
        
        ## Functions 
        if isinstance(e, Lambda):
            return Closure(e.var, env.copy(), e.body)

        if isinstance(e, Application):
            logger.info(f"IN APP WITH: {e}")
            oper = self._eval(e.operator, env)

            if not isinstance(oper, Closure):
                raise RuntimeError(f"Expected a closure, found: {oper}")
            operand = self._eval(e.operand, env)
            logger.info(f"\nAPPLYING CLOSURE: \n({oper}, \n{operand})")

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
            b = self._eval(e.test, env)
            if not isinstance(b, VNothing()) and not (isinstance(b, VBoolean) and not b.value):
                return self._eval(e.consequent, env)
            return self._eval(e.else_expr, env)
                    
        
        ## Numbers
        if isinstance(e, Plus):
            n1 = self._eval(e.e1, env)
            n2 = self._eval(e.e2, env)
            if not (isinstance(n1, VNumber) and isinstance(n2, VNumber)):
                raise RuntimeError(f"Expected numbers, got {n1}, {n2}")
            else:
                ty = merge_numeric_types(n1.type, n2.type)
                return VNumber(n1.value + n2.value, ty)
        if isinstance(e, Times):
            n1 = self._eval(e.e1, env)
            n2 = self._eval(e.e2, env)
            if not (isinstance(n1, VNumber) and isinstance(n2, VNumber)):
                raise RuntimeError(f"Expected numbers, got {n1}, {n2}")
            else:
                ty = merge_numeric_types(n1.type, n2.type)
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
                ty = merge_numeric_types(n1.type, n2.type)
                return VNumber(n1.value / n2.value, ty)

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
            
        if isinstance(e, List):
            ans = []
            for a in e.values:
                ans.append(self._eval(a, env))
            return VList(ans, e.type)

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
        if isinstance(e, Empty):
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
            
from evaluating import Interpreter
from defs import *




i = Interpreter()


## Literals
exp0 = Literal("hello world!", TString())
assert "hello world!" == i.eval(exp0)
exp1 = Literal(True, TBoolean())
assert i.eval(exp1)
exp2 = Literal([4, -1, 9], TList(TInt))
assert [4, -1, 9] == i.eval(exp2)
exp3 = Literal(3/4, TRational())
assert 3/4 == i.eval(exp3)

## Boolean Operators

exp4 = Or(Literal(True,TBoolean()), Literal(False,TBoolean()))
exp5 = And(Literal(True,TBoolean()), Literal(False,TBoolean()))
exp6 = Not(exp5)
assert i.eval(exp4)
assert not i.eval(exp5)
assert i.eval(exp6)


## Numeric Operators
exp65 = Literal(3, TNum())
assert i.eval(exp65) == 3
exp7 = Plus(Literal(4, TInt()), Literal(3, TNum()))
exp8 = Divide(Literal(0, TNat()), Literal(4/3, TRational()))
assert i.eval(exp7) == 7
assert i.eval(exp8) == 0


## Let

exp10 = Let("x", TBoolean(), Literal(False, TBoolean()), Variable("x", TBoolean()))
assert i.eval(exp10) == False
exp11 = Let("x", TBoolean(), Literal(False, TBoolean()), 
           Or(Variable("x", TBoolean()), 
              Literal(True, TBoolean())))
assert i.eval(exp11) == True

## Closures

exp21 = Application(Lambda("x", TRational(), Plus(Literal(3, TInt()), Variable("x", TRational()))),
                    Let("y", TInt(), Literal(-1, TInt()), Plus(Variable("y", TInt()), Literal(4, TNat()))))

assert i.eval(exp21) == 6


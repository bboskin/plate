try:
   from lib import *
except:
   from .lib import *
   
from loguru import logger

i : Normalizer = Normalizer()


## Literals
exp0 = Literal("hello world!", TString())
exp0_p = i.eval(exp0)
assert isinstance(exp0_p, Literal)
assert exp0_p.val == "hello world!"


exp1 = Literal(True, TBoolean())
exp1_p : Literal = i.eval(exp1)
assert isinstance(exp1_p, Literal)
assert exp1_p.val

exp2 = Literal(-2, TRational())
exp2_p : Literal = i.eval(exp2)
assert isinstance(exp2_p, Literal)
assert exp2_p.val == -2

# exp3 = Literal(3/4, TRational())
# exp3_p = i.eval(exp3)
# assert isinstance(exp3_p, Literal)
# assert 3/4 == exp3_p.val

## Boolean Operators

exp4 = Or(Literal(True,TBoolean()), Literal(False,TBoolean()))
exp4_p = i.eval(exp4)
exp5 = And(Literal(True,TBoolean()), Literal(False,TBoolean()))
exp5_p = i.eval(exp5)
exp6 = Not(exp5)
exp6_p = i.eval(exp6)
assert isinstance(exp4_p, Literal)
assert exp4_p.val == True
assert isinstance(exp5_p, Literal)
assert exp5_p.val == False

assert isinstance(exp6_p, Literal)
assert exp6_p.val == True


## Numeric Operators
exp65 = Literal(3, TInt())
exp65_p = i.eval(exp65)

assert isinstance(exp65_p, Literal)
assert exp65_p.val == 3

exp7 = i.eval(Plus(Literal(4, TInt()), Literal(3, TNum())))
assert isinstance(exp7, Literal)
assert exp7.val == 7

# exp8 = i.eval(Times(Literal(4, TNat()), Literal(4/3, TRational())))
# assert isinstance(exp8, Literal)
# print(exp8)
# assert exp8.val == Fraction(16, 3)


## Let

exp10 = Let(Variable("x", TBoolean()), Literal(False, TBoolean()), Variable("x", TBoolean()))
exp10_p = i.eval(exp10)
assert isinstance(exp10_p, Literal)
assert exp10_p.val == False
exp11 = Let(Variable("x", TBoolean()), Literal(False, TBoolean()), 
           Or(Variable("x", TBoolean()), 
              Literal(True, TBoolean())))

exp11_p = i.eval(exp11)
assert isinstance(exp11_p, Literal)
assert exp11_p.val == True

## Closure

exp21 = Let(Variable("f", TFunction(TRational(), TRational())),
            Lambda([Variable("x", TRational())], Plus(Literal(3, TInt()), Variable("x", TRational()))), 
            Application(Variable("f", Type()),
                    Let(Variable("y", TInt()), Literal(-1, TInt()), Plus(Variable("y", TInt()), Literal(4, TNat())))))
exp21_p = i.eval(exp21)

assert isinstance(exp21_p, Literal)
assert exp21_p.val == 6


from loguru import logger
import sys

try:
    from .lib import *
except:
    from lib import *

logger.remove()


s1 = '"hello"'
p = Parser(s1)
s1 = p.parse_expr()
assert str(s1) == "(Literal hello)"


s2 = "[1,   2,   3  ]"
p = Parser(s2)
s2 = p.parse_expr()
assert str(s2) == "(List: [(Literal 1),(Literal 2),(Literal 3)])"


s3 = "let [x : Nat] be 3 in: x"
p = Parser(s3)
s3 = p.parse_expr()
assert str(s3) == "(let (Var x) be (Literal 3) in (Var x))"


s4 = 'let [x : Int] be -1 in: let [x : Nat] be 0 in: [x + y, "hello world"]'
p = Parser(s4)
s4 = p.parse_expr()
assert str(s4) == "(let (Var x) be (Literal -1) in (let (Var x) be (Literal 0) in (List: [((Var x) + (Var y)),(Literal hello world)])))"

s5 = '(1 + 3) % 2'
p = Parser(s5)
s5 = p.parse_expr()
assert str(s5) == "(((Literal 1) + (Literal 3)) % (Literal 2))"

s6 = 'if (1 == 2) then let [x : Nat] be (     1 *     0) in:      4 % x else false'
p = Parser(s6)
s6 = p.parse_expr()
assert str(s6) == "(if ((Literal 1) == (Literal 2)) then (let (Var x) be ((Literal 1) * (Literal 0)) in ((Literal 4) % (Var x))) else (Literal False))"


s7 = 'if (1 == 2) then let [   x : Nat] be (     1 *     0) in:      4 % x else false'
p = Parser(s7)
s7 = p.parse_expr()
assert str(s7) == "(if ((Literal 1) == (Literal 2)) then (let (Var x) be ((Literal 1) * (Literal 0)) in ((Literal 4) % (Var x))) else (Literal False))"


s8 = 'let [f : Nat -> Nat] be lambda [x : Nat] : 1 in: 5'
p = Parser(s8)
s8 = p.parse_expr()
assert str(s8) == "(let (Var f) be (lambda (Var x) : (Literal 1)) in (Literal 5))"



s9 = 'let [f : ([a : Nat] -> Nat)] be lambda [x : Nat] : (x + y) in: f(2)'
p = Parser(s9)
s9 = p.parse_expr()
assert str(s9) == "(let (Var f) be (lambda (Var x) : ((Var x) + (Var y))) in ((Var f) (Literal 2)))"


s10 = 'defunc foo : [x : Nat] -> Nat: x + 1'
p = Parser(s10)
s10 = p.parse_def()
assert str(s10) == '(defunc (Var foo) : (lambda (Var x) : ((Var x) + (Literal 1))))'

s11 = "defunc bar1 : [y : Int] -> [x : Nat] -> Int: x + y"
p = Parser(s11)
s11 = p.parse_def()
assert str(s11) == "(defunc (Var bar1) : (lambda (Var y) : (lambda (Var x) : ((Var x) + (Var y)))))"

# logger.add(sys.stdout, level="DEBUG")

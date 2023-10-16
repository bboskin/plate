from loguru import logger
import sys

try:
    from .lib import *
except:
    from lib import *

# logger.add(sys.stdout, level="DEBUG")

s1 = '"hello"'
p = Parser(s1)
print(p.parse_expr())

s2 = "[1,  2,    3  ]"
p.parsing = s2
print(p.parse_expr())

s3 = "let [x : Nat] be 3 in: x"
p.parsing = s3
print(p.parse_expr())

s4 = 'let [x : Int] be -1 in: let [x : Nat] be 0 in: [x + y, "hello world"]'
p.parsing = s4
print(p.parse_expr())

s5 = '(1 + 3) % 2'
p.parsing=s5
print(p.parse_expr())

s6 = 'if (1 == 2) then let [x : Nat] be (1 * 0) in: 4 % x else false'
p.parsing = s6
print(p.parse_expr())
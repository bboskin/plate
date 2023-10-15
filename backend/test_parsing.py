try:
    from .lib import *
except:
    from lib import *

s1 = "3 / 4"
p = Parser(s1)
print(p.parse_expr())
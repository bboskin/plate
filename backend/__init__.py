try:
    from lib import *
except:
    from .lib import *


e1 =  "1"
p = Parser()
print(p.parse_file(e1))

## stand-alone expressions that are strings    
LITERALS = ['nothing', 'true', 'false']

## prefix operators
PREFIX = ['not', 'let', 'if', 'lambda', 'print', 'return', 'just', 'car', 'cdr', 'length']

## Types
TYPES = ['Absurd', 'Rational', 'Int', 'Nat', 'String', 'Boolean',
         'Maybe', 'List',
         'Universe', 'Equal', 'Exists', 'Forall']

## definition keywords
DEFS = ['defunc', 'defrel', 'defconst']

INFIX = ['and', 'or', '+', '-', '*', '/', '%', '==', 'in', ]
## everything together
AllKeywords = LITERALS + PREFIX + TYPES + DEFS

## stand-alone expressions that are strings    
LITERALS = ['nothing', 'true', 'false']

## prefix operators
PREFIX = ['not', 'let', 'if', 'lambda', 'print', 'return', 'just', 'car', 'cdr', 'length']

## Types
TYPES = ['Absurd', 'Rational', 'Int', 'Nat', 'String', 'Boolean', 'Bool',
         'Maybe', 'List',
         'Universe', 'Equal', 'Exists', 'Forall']

## definition keywords
DEFS = ['defunc', 'defrel', 'defconst']

INFIX = ['and', 'or', '+', '-', '*', '/', '%', '==', 'contains']
## everything together
AllKeywords = LITERALS + PREFIX + TYPES + DEFS

DELIMS = " ]),:"

LETTERS = "abcdefghijklmnopqrstuvwxyz" 
NUMBERS = "01233456789"
SYMBOLS = "-_~"
VARCHARS = LETTERS + NUMBERS + SYMBOLS

def valid_variable_name(x : str):
    if len(x) == 0:
        return False
    if x in AllKeywords:
        return False
    if x[0] not in LETTERS:
        return False
    else:
        for c in x:
            if x not in VARCHARS:
                return False
        return True

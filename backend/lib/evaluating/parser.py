try:
    from ..defs import *
except:
    from defs import *

class Parser():
    def __init__(self, content=""):
        self.all_content = content
        self.parsing = content

        ## to use when we fix next()
        self.char_index = 0
        self.line_number = 1
        self.line_index = 1

    # find the next token (used when expecting a new Phrase or Expression)
    def next(self) -> str:
        ## todo fix this to manually count whitespace
        self.parsing = self.parsing.strip()
        i = self.parsing.find(" ")
        s = self.parsing[:i]
        if s == "":
            s = self.parsing
        return s
    
    ## move past the first token
    def skip(self):
        self.parsing = self.parsing[self.parsing.find(" "):].strip()
    
    ## calls helper function depending on keyword type
    def dispatch(self, token : str) -> Expr:
        if token in LITERALS:
            return self.parse_literal()
        elif token in TYPES:
            return self.parse_type()
        elif token in PREFIX:
            return self.parse_prefix(token)


    ###################################
    ## parsing literals
    ###################################

    def parse_list(self) -> Expr:
        raise NotImplementedError

    def parse_string(self) -> Expr:
        raise NotImplementedError

    def check_num(self, token) -> [bool, float]:
        try:
            v = float(token)
        except:
            return [False, 0.0]
        return [True, v]
    
    def parse_number(self, n) -> Expr:
        self.skip()
        n = float(n)
        if isinstance(n, int):
            if n > 0:
                return Literal(n, TNat())
            else:
                return Literal(n, TInt())
        else:
            return Literal(n, TRational())


    def parse_literal(self) -> Literal:
        s = self.next()
        self.skip()
        match s:
            case 'nothing':
                return ENothing()
            case 'true':
                return Literal(True, TBoolean())
            case 'false':
                return Literal(False, TBoolean())
        raise CompileError(f"Unknown Literal: {s}")

    def parse_id(self) -> Variable:
        self.parsing = self.parsing.strip()
        if self.parsing[0] != '[':
            raise SyntaxError(f"Expected id to start with '[', found {self.parsing[:10]}")
        close = self.parsing.find(']')
        if close < 0:
            raise SyntaxError("Missing closing bracket for id")
        s = self.parsing[1:close]
        s_parsed = s.replace(" ", "").split[":"]
        if len(s_parsed) != 2:
            raise SyntaxError(f"Expected 2 tokens in id, found {s}")
        if s[0] in AllKeywords:
            raise SyntaxError(f"Keyword cannot be used for variable name")
        else:
            var = s[0]
            type_start = self.parsing.find(":") + 1
            self.parsing = self.parsing[type_start:]
            type = self.parse_type()
            self.parsing = self.parsing[1:]
            return Variable(var, type)


    ###########################
    ## Prefix Operators
    ###########################

    def parse_if(self) -> If:
        k =- self.next()
        if k != "if":
            raise CompileError(f'Expected if, found {k}')
        self.parsing = self.parsing[2:].strip()
        test : Expr = self.parse_expr()
        then = self.next()
        if then != "then":
            raise SyntaxError(f"Expected 'then' in if expression, found {then}")
        self.parsing = self.parsing[4:].strip()
        then : Expr = self.parse_expr()
        els = self.next()
        if els != "else":
            raise SyntaxError(f"Expected 'else' in if expression, found {els}")
        els : Expr = self.parse_expr()
        return If(test, then, els)

    def parse_let(self) -> Let:
        k = self.next()
        if k != "let":
            raise CompileError(f"Expected let, found {k}")
        else:
            self.parsing = self.parsing[3:].strip()
            id : Variable = self.parse_id()
            eq = self.next()
            if eq != "be":
                raise SyntaxError(f"Expected 'be' after let identified, found {eq}")
            self.parsing = self.parsing[self.parsing.find("be") + 1:]
            bind : Expr = self.parse_expr()
            colon = self.next()
            
            if colon != ":":
                raise SyntaxError(f"Expected ':' after let binding expression, found {colon}")
            self.parsing = self.parsing[self.parsing.find(":")+1:]
            body = self.parse_expr()

            return Let(id, bind, body)
        
    def parse_lambda(self) -> Lambda:
        l = self.next()
        if l != 'lambda':
            raise CompileError(f"Expected lambda, found {l}")
        self.skip()
        args = []
        while self.next() != ":":
            id = self.parse_id()
            args.append(id)
        if len(args) == 0:
            raise SyntaxError(f"Expected at least one argument for lambda, got none")
        body = self.parse_expr()
        return Lambda(args, body)

    def parse_print(self) -> PrintThen:
        p = self.next()
        if p != "print":
            raise CompileError(f"Expected print, found {p}")
        self.skip()
        msg = self.parse_expr()
        body = self.parse_expr()
        return PrintThen(msg, body)
            
    def parse_prefix(self, token : str) -> Expr:
        match token:
            case "if":
                return self.parse_if()
            case "let":
                return self.parse_let()
            case 'lambda':
                return self.parse_lambda()
            case 'print':
                return self.parse_print()
            case _:
                self.skip()
                e : Expr = self.parse_expr()
                match token:
                    case 'not':
                        return Not(e)
                    case 'just':
                        return Just(e)
                    case 'car':
                        return Car(e)
                    case 'cdr':
                        return Cdr(e)
                    case 'length':
                        return Length(e)

    ##############################
    ## Parsing Types
    ##############################

    def parse_tlist(self) -> TList:
        l = self.next()
        if l != "List":
            raise CompileError(f"Expected 'List' in type, found {l}")
        self.skip()
        t : Type = self.parse_type()
        return TList(t)

    
    def parse_maybe(self) -> TMaybe:
        l = self.next()
        if l != "Maybe":
            raise CompileError(f"Expected 'Maybe' in type, found {l}")
        self.skip()
        t : Type = self.parse_type()
        return TMaybe(t)
    
    def parse_universe(self) -> TUniverse:
        l = self.next()
        if l != "Universe":
            raise CompileError(f"Expected 'Universe' in type, found {l}")
        self.skip()
        e : Expr = self.parse_expr()
        return TUniverse(e)
    
    def parse_equal(self) -> TEqual:
        l = self.next()
        if l != "Equal":
            raise CompileError(f"Expected 'Equal' in type, found {l}")
        self.skip()
        t : Type = self.parse_type()
        e1 : Expr = self.parse_expr()
        e2 : Expr = self.parse_expr()
        return TEqual(t, e1, e2)
    
    def parse_exists(self) -> TExists:
        l = self.next()
        if l != "Exists":
            raise CompileError(f"Expected 'Exists' in type, found {l}")
        self.skip()
        x : Variable = self.parse_id()
        t : Type = self.parse_type()
        return TExists(x, t)
    
    def parse_function(self) -> TFunction:
        raise NotImplementedError
    
    def parse_forall(self) -> TFunction:
        raise NotImplementedError
    
    def parse_single_type(self) -> Type:
        token = self.next()
        match token:
            case "Absurd":
                self.skip()
                return TAbsurd()
            case "Rational":
                self.skip()
                return TRational()
            case "Int":
                self.skip()
                return TInt()
            case "Nat":
                self.skip()
                return TNat()
            case "String":
                self.skip()
                return TString()
            case "Boolean" | "Bool":
                self.skip()
                return TBoolean()
            case "List":
                return self.parse_tlist()
            case "Maybe":
                return self.parse_maybe()
            case "Universe":
                return self.parse_universe()
            case "Equal":
                return self.parse_equal()
            case "Exists":
                return self.parse_exists()
            case "Forall":
                return self.parse_forall()
            
    def parse_type(self) -> Type:
        t : Type = self.parse_single_type()
        op = self.next()
        if op == "->":
            self.skip()
            t2 : Expr = self.parse_type()
            t : Type = TFunction(t, t2)
        return t

    ###########################
    ## General-Case parsing
    ###########################


    def parse_paren(self) -> Expr:
        if self.parsing[0] != "(":
            raise CompileError(f"Expected to be at open paren, found {self.parsing[:10]}")
        self.parsing = self.parsing[1:]
        expr : Expr = self.parse_expr()
        self.parsing = self.parsing[self.parsing.find(")")+1:]
        return expr

    def join_infix(self, e1 : Expr, op : str, e2 : Expr) -> Expr:
        match op:
            case "and":
                return And(e1, e2)
            case 'or':
                return Or(e1, e2)
            case "+":
                return Plus(e1, e2)
            case "-":
                return Plus(e1, Times(Literal(-1, TInt()), e2))
            case "/":
                return Divide(e1, e2)
            case "%":
                return Mod(e1, e2)
            case "in":
                return In(e1, e2)
        raise CompileError(f"Unknown Infix Operator: {op}")

    def parse_single_expr(self) -> Expr:
        token = self.next()
        if token in AllKeywords:
            return self.dispatch(token)
        elif "\"" == token[0]:
            return self.parse_string()
        elif "(" == token[0]:
            return self.parse_paren()
        elif "[" == token[0]:
            return self.parse_list()
        else:
            is_num = self.check_num(token)
            if is_num[0]:
                return self.parse_number(is_num[1])
            else:
                self.skip()
                return Variable(token)
    

    # it's either a single expression, or two expressions joined by an infix operator
    def parse_expr(self) -> Expr:
        e = self.parse_single_expr()
        if not e:
            return False
        op = self.next()
        if op in INFIX:
            self.skip()
            e2 : Expr = self.parse_expr()
            e : Expr = self.join_infix(e, op, e2)
        return e


    ###############################
    ## Top-Level definitions
    ###############################
    def parse_defrel(self):
        raise NotImplementedError
    
    def parse_defconst(self):
        token = self.next()
        if token != "defconst":
            raise CompileError(f"Expected defconst, found {token}")
        self.skip()
        var : Variable = self.parse_id()
        exp : Expr = self.parse_expr()
        return Defconst(var, exp)

    def parse_defunc(self):
        token = self.next()
        if token != "defunc":
            raise CompileError(f"Expected defunc, found {token}")
        self.skip()
        name : str = self.next()
        if name in AllKeywords:
            raise SyntaxError(f"Cannot use keyword {name} for top-level function")
        self.skip()
        colon = self.next()
        if colon != ":":
            raise SyntaxError(f"Expected colon after defunc name, found {colon}")
        self.parsing = self.parsing[self.parsing.find(":")+1:]
        ty = self.parse_type()
        colon = self.next()
        if colon != ":":
            raise SyntaxError(f"Expected colon after defunc type, found {colon}")
        self.parsing = self.parsing[self.parsing.find(":")+1:]
        exp : Expr = self.parse_expr()
        return Defunc(name, ty, exp)

    def parse_def(self, token) -> Def:
        match token:
            case 'defunc':
                return self.parse_defunc()
            case 'defrel':
                return self.parse_defrel()
            case 'defconst':
                return self.parse_defconst()
        raise CompileError(f"Unknown Definition Keyword: {token}")

    def parse_file(self) -> list[Expr]:
        ans = []
        while len(self.parsing) > 0:
            self.parsing = self.parsing.strip()
            t = self.next()
            if t in DEFS:
                ans.append(self.parse_def(t))
            ans.append(self.parse_expr())
            self.parsing = self.parsing.strip()
        return []
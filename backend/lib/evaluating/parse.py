from loguru import logger
from fractions import Fraction

try:
    from ..defs import *
except:
    from defs import *

class Parser():
    def __init__(self, content=""):
        self.parsing = content

        self.total_chars = len(self.parsing)
        ## to use when we fix next()
        self.char_index = 0
        self.line_number = 1
        self.line_index = 1


    def eoe(self) -> int:
        i = self.total_chars
        for c in DELIMS:
            j = self.parsing.find(c)
            if j > 0:
                i = min(i, j)
                # logger.info(f"Using {c} : {i} in {self.parsing} as delimiter")
        return i


    # find the next token (used when expecting a new Phrase or Expression)
    def next(self) -> str:
        ## todo fix this to manually count whitespace
        
        self.parsing = self.parsing.strip()
        i = self.eoe()
        
        s = self.parsing[:i]

        # logger.debug(f"Next finds: {s}")
        return s.strip()
    
    ## move past the first token
    def skip(self):
        i = self.eoe()
        self.parsing = self.parsing[i:].strip()
    
    ## calls helper function depending on keyword type
    def dispatch(self, token : str) -> Expr:
        # logger.debug("calling dispatch")
        if token in LITERALS:
            return self.parse_literal()
        elif token in TYPES:
            return self.parse_type()
        elif token in PREFIX:
            return self.parse_prefix(token)


    ###################################
    ## parsing literals
    ###################################

    def parse_list(self) -> List:
        # logger.debug("calling parse list")
        bracket = self.parsing[0]
        if bracket != "[":
            raise CompileError(f"Expected bracket to start list parsing, found {bracket}")
        self.parsing = self.parsing[1:].replace(",", " , ")
        es = []

        while self.parsing[0] != "]":
            e = self.parse_expr()
            es.append(e)
            end = self.parsing.find(']')
            comma = self.parsing.find(",")
            if comma < end:
                
                self.parsing = self.parsing[comma +1:]
            else:
                break
            
        self.parsing = self.parsing[self.parsing.find("]")+1:]
        res = List(es)
        # logger.debug(res)
        return res

    def parse_string(self) -> Expr:
        # logger.debug("calling parse string")
        quote = self.parsing[0]
        if quote != "\"":
            raise CompileError(f"Expected double quote for string literal, found {quote}")
        self.parsing = self.parsing[1:]
        loc = self.parsing.find("\"")
        word = self.parsing[0:loc]
        self.parsing = self.parsing[loc+1:]
        res = Literal(word, TString())
        # logger.debug(res)
        return res

    def check_num(self, token) -> [bool, float]:
        try:
            v = float(token)
        except:
            return [False, 0.0]
        return [True, v]
    
    def parse_number(self, n) -> Expr:
        # logger.debug("calling parse number")
        self.skip()
        n = float(n)
        if n % 1 == 0:
            n = int(n)
            if n > 0:
                res = Literal(n, TNat())
            else:
                res = Literal(n, TInt())
        else:
            n = Fraction(n)
            res = Literal(n, TRational())
        # logger.debug(res)
        return res

    def parse_literal(self) -> Literal:
        # logger.debug("calling parse literal")
        s = self.next()
        self.skip()
        res = False
        match s:
            case 'qed':
                res = QED()
            case 'nothing':
                res = ENothing()
            case 'true':
                res = Literal(True, TBoolean())
            case 'false':
                res = Literal(False, TBoolean())
        # logger.debug(res)
        if res != False:
            return res
        raise CompileError(f"Unknown Literal: {s}")

    def parse_id(self) -> Variable:
        # logger.debug("calling parse id")
        self.parsing = self.parsing.strip()
        if self.parsing[0] != '[':
            raise SyntaxError(f"Expected id to start with '[', found {self.parsing[:10]}")
        
        self.parsing = self.parsing[1:]
        var = self.next()
        if var in AllKeywords:
            raise SyntaxError(f"Keyword cannot be used in id: {var}")
        self.skip()
        close = self.parsing.find("]")
        colon = self.parsing.find(":")
        if close < colon:
            raise SyntaxError(f"Expected : before type in ID, found {self.parsing[:20]}")
        self.parsing = self.parsing[colon+1:]
        #logger.debug(self.parsing)
        ty = self.parse_type()
        #logger.debug(ty)
        close = self.parsing.find("]")
        self.parsing = self.parsing[close+1:]
        res = Variable(var, ty)
        # logger.debug(res)
        return res


    ###########################
    ## Prefix Operators
    ###########################

    def parse_if(self) -> If:
        # logger.debug("calling parse if")
        k = self.next()
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
        self.skip()
        els : Expr = self.parse_expr()
        res = If(test, then, els)
        # logger.debug(res)
        return res
    
    def parse_induct(self) -> Induct:
        k = self.next()
        if k != "induct":
            raise CompileError(f'Expected induct, found {k}')
        self.parsing = self.parsing[6:].strip()
        arg : Expr = self.parse_expr()
        out_type : Expr = self.parse_expr()
        base : Expr = self.parse_expr()
        
        inds = []
        next_ind = self.parse_expr()
        while not isinstance(next_ind, QED):
            # logger.info(type(next_ind))
            inds.append(next_ind)
            next_ind = self.parse_expr()
        
        
        res = Induct(arg, out_type, base, inds)
        #logger.debug(res)
        return res

    def parse_let(self) -> Let:
        #logger.debug("calling parse let")
        #logger.debug(self.parsing)
        k = self.next()
        if k != "let":
            raise CompileError(f"Expected let, found {k}")
        else:
            self.skip()
            #logger.debug(self.parsing)
            id : Variable = self.parse_id()
            #logger.info(f"Let bind id = {id}")
            #logger.debug(self.parsing)
            eq = self.next()
            if eq != "be":
                #logger.debug(self.parsing)
                raise SyntaxError(f"Expected 'be' after let identifier, found {eq}")
            self.skip()
            #logger.debug(f"Parsing Bind with: {self.parsing}")
            bind : Expr = self.parse_expr()
            #logger.debug(bind)
            in_ = self.next()
            if in_ != "in":
                raise SyntaxError(f"Expected 'in' after let binding expression, found {in_}")
            
            self.parsing = self.parsing[self.parsing.find(":")+1:]
            body = self.parse_expr()
            res = Let(id, bind, body)
            # logger.debug(res)
            return res
        
    def parse_lambda(self) -> Lambda:
        #logger.debug("calling parse lambda")
        l = self.next()
        if l != 'lambda':
            raise CompileError(f"Expected lambda, found {l}")
        self.skip()
        args = []
        while self.next() != ":":
            id = self.parse_id()
            args.append(id)
        #logger.debug([str(arg) for arg in args])
        if len(args) == 0:
            raise SyntaxError(f"Expected at least one argument for lambda, got none")
        colon = self.next()
        if colon != ":":
            raise SyntaxError(f"Expected a colon before lambda body, found {colon}")
        self.skip()
        body = self.parse_expr()
        res = Lambda(args, body)
        # logger.debug(res)
        return res

    def parse_print(self) -> PrintThen:
        #logger.debug("calling parse print")
        p = self.next()
        if p != "print":
            raise CompileError(f"Expected print, found {p}")
        self.skip()
        msg = self.parse_expr()
        body = self.parse_expr()
        res = PrintThen(msg, body)
        # logger.debug(res)
        return res
            
    def parse_prefix(self, token : str) -> Expr:
        #logger.debug("calling parse prefix")
        match token:
            case "induct":
                res = self.parse_induct()
            case "if":
                res = self.parse_if()
            case "let":
                res = self.parse_let()
            case 'lambda':
                res = self.parse_lambda()
            case 'print':
                res = self.parse_print()
            case _:
                self.skip()
                e : Expr = self.parse_expr()
                match token:
                    case 'not':
                        res = Not(e)
                    case 'just':
                        res = Just(e)
                    case 'car':
                        res = Car(e)
                    case 'cdr':
                        res = Cdr(e)
                    case 'length':
                        res = Length(e)
        # logger.debug(res)
        return res

    ##############################
    ## Parsing Types
    ##############################

    def parse_tlist(self) -> TList:
        #logger.debug("calling parse tlist")
        l = self.next()
        if l != "List":
            raise CompileError(f"Expected 'List' in type, found {l}")
        self.skip()
        t : Type = self.parse_type()
        res = TList(t)
        # logger.debug(res)
        return res

    
    def parse_maybe(self) -> TMaybe:
        #logger.debug("calling parse tmaybe")
        l = self.next()
        if l != "Maybe":
            raise CompileError(f"Expected 'Maybe' in type, found {l}")
        self.skip()
        t : Type = self.parse_type()
        res = TMaybe(t)
        # logger.debug(res)
        return res
    
    def parse_universe(self) -> TUniverse:
        #logger.debug("calling parse universe")
        l = self.next()
        if l != "Universe":
            raise CompileError(f"Expected 'Universe' in type, found {l}")
        self.skip()
        e : Expr = self.parse_expr()
        res = TUniverse(e)
        # logger.debug(res)
        return res
    
    def parse_equal(self) -> TEqual:
        #logger.debug("calling parse equal")
        l = self.next()
        if l != "Equal":
            raise CompileError(f"Expected 'Equal' in type, found {l}")
        self.skip()
        t : Type = self.parse_type()
        e1 : Expr = self.parse_expr()
        e2 : Expr = self.parse_expr()
        res = TEqual(t, e1, e2)
        # logger.debug(res)
        return res
    
    def parse_exists(self) -> TExists:
        #logger.debug("calling parse exists")
        l = self.next()
        if l != "Exists":
            raise CompileError(f"Expected 'Exists' in type, found {l}")
        self.skip()
        x : Variable = self.parse_id()
        t : Type = self.parse_type()
        res = TExists(x, t)
        # logger.debug(res)
        return res
    
    def parse_function(self) -> TFunction:
        #logger.debug("calling parse function")
        raise NotImplementedError
    
    def parse_forall(self) -> TFunction:
        #logger.debug("calling parse forall")
        raise NotImplementedError
    
    def parse_single_type(self) -> Type:
        #logger.debug("calling parse single type")
        token = self.next()
        res = False
        if token[0] == "[":
            id = self.parse_id()
            arrow = self.next()
            if arrow != "->":
                raise SyntaxError(f"Expected -> after id while parsing type, found {arrow}")
            self.skip()
            e2 = self.parse_type()
            res = TFunction(id, e2)
        else:
            match token:
                case "Absurd":
                    self.skip()
                    res = TAbsurd()
                case "Rational":
                    self.skip()
                    res = TRational()
                case "Int":
                    self.skip()
                    res = TInt()
                case "Nat":
                    self.skip()
                    res = TNat()
                case "String":
                    self.skip()
                    res = TString()
                case "Boolean" | "Bool":
                    self.skip()
                    res = TBoolean()
                case "List":
                    res = self.parse_tlist()
                case "Maybe":
                    res = self.parse_maybe()
                case "Universe":
                    res = self.parse_universe()
                case "Equal":
                    res = self.parse_equal()
                case "Exists":
                    res = self.parse_exists()
                case "Forall":
                    res = self.parse_forall()
        # logger.info(res)
        return res
            
    def parse_type(self) -> Type:
        # logger.debug(f"calling parse type on {self.parsing}")
        t : Type = self.parse_single_type()
        op = self.next()
        if op == "":
            pass
        elif op[0] == "(":
            self.parsing = self.parsing[1:]
            t = self.parse_type()
            self.parsing = self.parsing[self.parsing.find(")")+1:]
            op = self.next()
            
        if op == "->":
            self.skip()
            t2 : Expr = self.parse_type()
            t : Type = TFunction(t, t2)
        # logger.info(t)
        return t

    ###########################
    ## General-Case parsing
    ###########################
    def parse_app(self, f : Expr) -> Expr:
        a = False
        while self.next()[0] != ")":
            a = self.parse_expr()
            # logger.debug(f"Found arg: {a}")
            f = Application(f, a)
            self.parsing = self.parsing.strip()
        
        if isinstance(a, bool):
            raise SyntaxError()
        self.parsing = self.parsing[1:]
        # logger.debug(f)
        return f
    
    def parse_paren(self) -> Expr:
        #logger.debug("calling parse paren")
        if self.parsing[0] != "(":
            raise CompileError(f"Expected to be at open paren, found {self.parsing[:10]}")
        self.parsing = self.parsing[1:]
        expr : Expr = self.parse_expr()
        self.parsing = self.parsing[self.parsing.find(")")+1:]
        # logger.debug(expr)
        return expr

    def join_infix(self, e1 : Expr, op : str, e2 : Expr) -> Expr:
        #logger.debug("calling join infix")
        match op:
            case "and":
                return And(e1, e2)
            case 'or':
                return Or(e1, e2)
            case "+":
                return Plus(e1, e2)
            case "*":
                return Times(e1, e2)
            case "-":
                return Plus(e1, Times(Literal(-1, TInt()), e2))
            case "/":
                return Divide(e1, e2)
            case "%":
                return Mod(e1, e2)
            case "contains":
                return Contains(e1, e2)
            case "==":
                return Equal(e1, e2)
        raise CompileError(f"Unknown Infix Operator: {op}")

    def parse_single_expr(self) -> Expr:
        #logger.debug(f"calling parse single expr on {self.parsing}")
        token = self.next()
        #logger.debug(f"TOKEN: {token}")
        if token in AllKeywords:
            return self.dispatch(token)
        elif "\"" == token[0]:
            return self.parse_string()
        elif "(" == token[0]:
            return self.parse_paren()
        elif "[" == token[0]:
            return self.parse_list()
        elif "(" == token[-1]:
            f = token[:-1]
            self.parsing = self.parsing[self.parsing.find("(")+1:]
            return self.parse_app(f)
        else:
            is_num = self.check_num(token)
            if is_num[0]:
                return self.parse_number(is_num[1])
            else:
                if "(" in token:
                    loc = token.find("(")
                    f = Variable(token[:loc], Type())
                    self.parsing = self.parsing[loc+1:]
                    return self.parse_app(f)
                if valid_variable_name(token):
                    self.skip()
                    return Variable(token)
                else:
                    return False
    

    # it's either a single expression, or two expressions joined by an infix operator
    def parse_expr(self) -> Expr:
        #logger.debug(f"calling parse expression {self.parsing}")
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
        #logger.debug("calling parse defrel")
        raise NotImplementedError
    
    def parse_defconst(self):
        #logger.debug("calling parse defconst")
        token = self.next()
        if token != "defconst":
            raise CompileError(f"Expected defconst, found {token}")
        self.skip()
        var : Variable = self.parse_id()
        #logger.info(var)
        #logger.info(f"calling parse expr on {self.parsing}")
        exp : Expr = self.parse_expr()
        #logger.info(exp)
        return Defconst(var, exp)

    def parse_defunc(self):
        #logger.debug("calling parse defunc")
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
        #logger.info(ty)
        if not isinstance(ty, TFunction):
            raise SyntaxError(f"Expected a function type for defunc, got {ty}")
        f_ty = ty
        args = []
        #logger.debug(f_ty)
        while isinstance(f_ty, TFunction):
            args.append(f_ty.input)
            f_ty = f_ty.output
        #logger.debug(args)
        exp = Lambda(args, exp)
        res = Defunc(Variable(name, ty), exp)
        #logger.debug(res)
        return res

    def parse_def(self) -> Def:
        # logger.debug("calling parse def")
        token = self.next()
        match token:
            case 'defunc':
                return self.parse_defunc()
            case 'defrel':
                return self.parse_defrel()
            case 'defconst':
                return self.parse_defconst()
        raise CompileError(f"Unknown Definition Keyword: {token}")

    def parse_file(self) -> list[Expr]:
        #logger.debug("calling parse file")
        ans = []
        while len(self.parsing) > 0:
            self.parsing = self.parsing.strip()
            t = self.next()
            if t in DEFS:
                ans.append(self.parse_def())
            else:
                ans.append(self.parse_expr())
            self.parsing = self.parsing.strip()
        return ans
    
if __name__ == "__main__":
    p = Parser("[y : Int] -> [x : Nat] -> Int")
    print(p.parse_type())
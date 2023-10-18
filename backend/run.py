from argparse import ArgumentParser
from lib import Parser, Interpreter
from loguru import logger

if __name__ == "__main__":
    p : ArgumentParser = ArgumentParser()
    p.add_argument('file')
    args = p.parse_args()
    fname = args.file
    with open(fname, 'r') as f:
        exp = f.read()
        pars = Parser(exp)
        interp = Interpreter()
        es = pars.parse_file()
        logger.info([str(e) for e in es])
        ρ = interp.init_env(es)
        logger.info(str(ρ))
        vs = interp.eval_file(es, ρ)
    for v in vs:
        print(v)

# if __name__ == "__main__":
#     p = Parser("List Nat")
#     # p = Parser("[x : Nat] -> Int")
#     print(p.parse_type())
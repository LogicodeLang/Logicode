import os
import re
import operator as op
import argparse
from random import randint

if not hasattr(__builtins__, "raw_input"):
    raw_input = input
if not hasattr(__builtins__, "basestring"):
    basestring = str

regex = re._pattern_type

rWhitespace = re.compile(r"[ \t]+", re.M)
rCommandSeparator = re.compile(r"[\r\n;]+", re.M)
rBits = re.compile(r"[01]+")
rName = re.compile(r"(?!\binput\b|\b__scope__\b)[a-zA-Z_$]+")
rRandom = re.compile(r"\?")
rInput = re.compile(r"\binput\b")
rScope = re.compile(r"\b__scope__\b")
rInfix = re.compile(r"[&|]")
rPrefix = re.compile(r"!")
rPostfix = re.compile(r"\[[ht]\]")
rOpenParenthesis = re.compile(r"\(")
rCloseParenthesis = re.compile(r"\)")
rOpenBracket = re.compile(r"\[")
rCloseBracket = re.compile(r"\]")
rCircuit = re.compile(r"\bcirc\b")
rVariable = re.compile(r"\bvar\b")
rCondition = re.compile(r"\bcond\b")
rOut = re.compile(r"out ")
rComment = re.compile(r"#.*")
rLambda = re.compile(r"->")
rOr = re.compile(r"/")
rComma = re.compile(r",")
rEquals = re.compile(r"=")
rPlus = re.compile(r"\+")

rLinestart = re.compile("^", re.M)
rGetParentFunctionName = re.compile("<function ([^.]+)")

# Parser functions

def Noop(argument):
    return argument


def NoLambda(result):
    return lambda scope: None


def Bits(result):
    value = list(map(lambda char: int(char), result[0]))
    return lambda scope: value


def Name(result):
    return lambda scope: scope[result[0]]


def Random(result):
    return lambda scope: [randint(0, 1)]


def Input(result):
    return lambda scope: [GetInput(scope)]


def ScopeTransform(result):
    return lambda scope: Print(repr(scope))


def Literal(result):
    return [result]


def Arguments(result):
    arguments = result[1]
    if len(arguments):
        arguments = arguments[0]
        if (isinstance(arguments, list) and isinstance(arguments[-1], list) and len(arguments[-1])
               and len(arguments[-1][0]) == 2):
            arguments = arguments[:-1] + list(map(lambda l: l[1], arguments[1]))
    if len(arguments) and isinstance(arguments[-1], list) and not len(arguments[-1]):
        arguments = arguments[:-1]
    return lambda scope: arguments


def Expression(result):
    length = len(result)
    if length == 1 and hasattr(result[0], "__call__"):
        result = result[0]
        while isinstance(result, list) and len(result) == 1:
            result = result[0]
        return result
    result = result[0][0]
    length = len(result)
    if length == 3:
        if (isinstance(result[0], basestring) and rOpenParenthesis.match(result[0])):
            return result[1]
        operator = result[1]
        if isinstance(operator, basestring) and rPlus.match(operator):
            return lambda scope: result[0](scope) + result[2](scope)
        if isinstance(operator, basestring) and rInfix.match(operator):
            if operator == "&":
                return lambda scope: list(map(op.and_, result[0](scope), result[2](scope)))
            if operator == "|":
                return lambda scope: list(map(op.or_, result[0](scope), result[2](scope)))
    if length == 2:
        operator = result[0]
        if isinstance(operator, basestring) and rPrefix.match(operator):
            if operator == "!":
                return lambda scope: list(map(int, map(op.not_, result[1](scope))))
        if isinstance(result[1], list):
            operator = result[1][0][0]
            if isinstance(operator, basestring) and rPostfix.match(operator):
                if operator == "[h]":
                    return lambda scope: [result[0](scope)[0]]
                if operator == "[t]":
                    return lambda scope: [result[0](scope)[-1]]
        # Function call
        name = result[0]
        args = result[1]
        return lambda scope: name(scope)(list(map(lambda arg: arg(scope), args(scope))))
    if length == 1:
        return result[0]


def Circuit(result):
    name = result[1]
    arguments = result[2]
    body = result[4]
    if isinstance(body, list):
        expressions = map(lambda l: l[0], body[0][1])
        body = lambda scope: list(filter(None, map(lambda expression: expression(scope), expressions)))[-1]
    return lambda scope: scope.set(name, lambda args: body(Inject(Scope(scope), arguments(scope), args)))


def Variable(result):
    name = result[1]
    value = result[3]
    return lambda scope: scope.set(name, value(scope))


def Condition(result):
    condition = result[1]
    if_true = result[3]
    if_false = result[5]
    return lambda scope: (if_true(scope) if condition(scope)[0] else if_false(scope))


def Out(result):
    return lambda scope: Print(result[1](scope))


def GetInput(scope):
    if not len(scope["input"]):
        scope["input"] = list(map(int, filter(lambda c: c == "0" or c == "1", raw_input("Input: "))))[::-1]
    return scope["input"].pop()


def Print(result):
    if result:
        print("".join(list(map(str, result))))
        
# Scope stuff

def getParentFunctionName(lambda_function):
    return rGetParentFunctionName.match(repr(lambda_function)).group(1)

def islambda(v):
  LAMBDA = lambda:0
  return isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__

class Scope:
    def __init__(self, parent={}):
        self.parent = parent
        self.lookup = {}

    def __contains__(self, key):
        return key in self.parent or key in self.lookup

    def __getitem__(self, key):
        if key in self.lookup:
            return self.lookup[key]
        else:
            return self.parent[key]

    def __setitem__(self, key, value):
        if key in self.lookup:
            self.lookup[key] = value
        elif key in self.parent:
            self.parent[key] = value
        else:
            self.lookup[key] = value

    def __delitem__(self, key):
        if key in self.lookup:
            del self.lookup[key]
        else:
            del self.parent[key]

    def __repr__(self):
        string = "{"
        for key in self.lookup:
            value = self.lookup[key]
            string += "%s: %s" % (key,
                (getParentFunctionName(value) if islambda(value) else "".join(list(map(str, value)))
                 if isinstance(value, list) else repr(value)))
            string += ", "
        string = string[:-2] + "}"
        return (string +
            "\n" +
            rLinestart.sub("    ", repr(self.parent)))

    def has(self, key):
        return key in self

    def get(self, key):
        return self[key]

    def set(self, key, value):
        self[key] = value

    def delete(self, key):
        del self[key]
        

# Dictionaries:

# Grammars
grammars = {
    "CommandSeparator": [rCommandSeparator],
    "Bits": [rBits],
    "Name": [rName],
    "Random": [rRandom],
    "Input": [rInput],
    "Scope": [rScope],
    "Literal": [["|", "Input", "Scope", "Bits", "Name", "Random"]],
    "Arguments": [
        rOpenParenthesis,
        ["?", rName, ["*", rComma, rName]],
        rCloseParenthesis
    ],
    "Call Arguments": [
        rOpenParenthesis,
        ["?", "Expression", ["*", rComma, "Expression"]],
        rCloseParenthesis
    ],
    "Term": [
        [
            "|",
            ["1", rOpenParenthesis, "Expression", rCloseParenthesis],
            "Literal"
        ]
    ],
    "Alpha": [
        [
            "|",
            ["1", rPrefix, "Term"],
            ["1", "Name", "Call Arguments"],
            ["1", rOpenParenthesis, "Expression", rCloseParenthesis],
            "Literal"
        ]
    ],
    "Expression": [
        [
            "|",
            ["1", "Alpha", rInfix, "Expression"],
            ["1", rPrefix, "Term"],
            ["1", "Alpha", ["+", rPostfix]],
            ["1", "Name", "Call Arguments"],
            ["1", rOpenParenthesis, "Expression", rCloseParenthesis],
            "Literal"
        ]
    ],
    "TopLevelExpression": [
        [
            "|",
            ["1", "Expression", rPlus, "TopLevelExpression"],
            ["1", "Expression"]
        ]
    ],
    "Circuit": [
        rCircuit,
        rName,
        "Arguments",
        rLambda,
        [
            "|",
            "TopLevelExpression",
            "Variable",
            "Out",
            ["1", rOpenBracket, ["+", ["|", "CommandSeparator", "Variable", "Out", "TopLevelExpression"]], rCloseBracket]
        ]
    ],
    "Variable": [rVariable, rName, rEquals, "TopLevelExpression"],
    "Condition": [
        rCondition,
        "TopLevelExpression",
        rLambda,
        ["|", "Variable", "Out"],
        rOr,
        ["|", "Variable", "Out"]
    ],
    "Out": [rOut, "TopLevelExpression"],
    "Comment": [rComment],
    "Program": [
        [
            "+",
            ["|", "CommandSeparator", "Comment", "Circuit", "Variable", "Condition", "Out", "TopLevelExpression"]
        ]
    ]
}

# Transforming grammars to functions
transform = {
    "CommandSeparator": NoLambda,
    "Bits": Bits,
    "Name": Name,
    "Random": Random,
    "Input": Input,
    "Scope": ScopeTransform,
    "Literal": Literal,
    "Arguments": Arguments,
    "Call Arguments": Arguments,
    "Term": Expression,
    "Alpha": Expression,
    "Expression": Expression,
    "TopLevelExpression": Expression,
    "Circuit": Circuit,
    "Variable": Variable,
    "Condition": Condition,
    "Out": Out,
    "Comment": NoLambda
}

# Mins and maxes
mins = {
    "?": 0,
    "*": 0,
    "+": 1
}

maxes = {
    "?": 1,
    "*": -1,
    "+": -1
}


def Inject(scope, keys, values):
    for key, value in zip(keys, values):
        scope.lookup[key] = value
    return scope


def Transform(token, argument):
    return (transform.get(token, Noop)(argument[0]), argument[1])


def NoTransform(token, argument):
    return argument


def Get(code, token, process=Transform):
    length = 0
    match = rWhitespace.match(code)
    if match:
        string = match.group()
        length += len(string)
        code = code[length:]

    if isinstance(token, list):
        first = token[0]
        rest = token[1:]
        if first == "|":
            for token in rest:
                result = Get(code, token, process)
                if result[0] != None:
                    return (result[0], result[1] + length)
            return (None, 0)
        minN = int(mins.get(first, first))
        maxN = int(maxes.get(first, first))
        result = []
        amount = 0
        while amount != maxN:
            tokens = []
            success = True
            for token in rest:
                gotten = Get(code, token, process)
                if gotten[0] == None:
                    success = False
                    break
                tokens += [gotten[0]]
                gottenLength = gotten[1]
                code = code[gottenLength:]
                length += gottenLength
            if not success:
                break
            result += [tokens]
            amount += 1
        if amount < minN:
            return (None, 0)
        return (result, length)

    if isinstance(token, basestring):
        result = []
        grammar = grammars[token]
        for tok in grammar:
            gotten = Get(code, tok, process)
            if gotten[0] == None:
                return (None, 0)
            result += [gotten[0]]
            gottenLength = gotten[1]
            code = code[gottenLength:]
            length += gottenLength
        return process(token, (result, length))

    if isinstance(token, regex):
        match = token.match(code)
        if match:
            string = match.group()
            return (string, len(string) + length)
        return (None, 0)


def Run(code="", input="", astify=False, grammar="Program", repl=False, scope=None):
    if not scope:
        scope = Scope()
    if repl:
        while repl:
            try:
                Print(Run(raw_input("Logicode> "), scope=scope))
            except (KeyboardInterrupt, EOFError):
                return
    scope["input"] = list(map(int, filter(lambda c: c == "0" or c == "1", input)))[::-1]
    if astify:
        result = Get(code, grammar, NoTransform)[0]
        print(Astify(result))
        return
    result = Get(code, grammar)[0]
    if result:
        program = result[0]
        for statement in program:
            result = statement[0](scope)
        return result


def Astify(parsed, padding=""):
    result = ""
    if isinstance(parsed, list):
        padding += " "
        for part in parsed:
            result += Astify(part, padding)
        return result
    else:
        return padding + str(parsed) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("-f", "--file", type=str, nargs="*", default="", help="File path of the program.")
    parser.add_argument("-c", "--code", type=str, nargs="?", default="", help="Code of the program.")
    parser.add_argument("-i", "--input", type=str, nargs="?", default="", help="Input to the program.")
    parser.add_argument("-a", "--astify", action="store_true", help="Print AST instead of interpreting.")
    parser.add_argument("-r", "--repl", action="store_true", help="Open as REPL instead of interpreting.")
    parser.add_argument("-t", "--test", action="store_true", help="Run unit tests.")
    argv = parser.parse_args()
    if argv.test:
        from test import *
        RunTests()
    elif argv.repl:
        Run(repl=True)
    elif len(argv.file):
        code = ""
        for path in argv.file:
            if os.path.isfile(argv.file[0]):
                with open(argv.file[0]) as file:
                    code += file.read() + "\n"
            else:
                with open(argv.file[0] + ".lgc") as file:
                    code += file.read() + "\n"
        if argv.astify:
            Run(code, "", True)
        elif argv.input:
            Run(code, argv.input)
        else:
            Run(code)
    elif argv.code:
        if argv.astify:
            Run(argv.code, "", True)
        elif argv.input:
            Run(argv.code, argv.input)
        else:
            Run(argv.code)
    else:
        code = raw_input("Enter program: ")
        if argv.astify:
            Run(code, "", True)
        elif argv.input:
            Run(code, argv.input[0])
        else:
            Run(code)

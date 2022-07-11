from collections import namedtuple
from abc import ABC, abstractmethod
from itertools import chain
from iteration_utilities import deepflatten

Token = namedtuple('Token', ['type', 'value', 'code'])
Token.__eq__ = lambda self, other: \
(
        self.type == other.type
    if
        self.type != '%Any%' and other.type != '%Any%'
    else
        True
) \
and (
        self.value == other.value
    if
        self.value != '%Any%' and other.value != '%Any%'
    else
        True
) \
and (
        self.code == other.code
    if
        self.code != -2 and other.code != -2
    else
        True
)

EOF = Token('EOF', 'EOF', -1)

operators = {
        '+': {'=', '+'},
        '-': {'=', '-'},
        '*': {'=', '*'},
        '/': {'=', '/'},
        '%': {'='},
        '&': {'&', '='},
        '|': {'|', '='},
        '^': {'='},
        '!': {'='},
        '<': {'=', '<'},
        '>': {'=', '>'},
        '=': {'=', '>'},
        '.': set(),
}

op_priority = {
    '+': 4,
    '-': 4,
    '*': 5,
    '/': 5,
    '%': 5,
    '**': 6,
    '//': 6,
    '++': 5,
    '--': 5,
    '&': 5,
    '|': 5,
    '^': 5,
    '<': 3,
    '>': 3,
    '<=': 3,
    '>=': 3,
    '==': 3,
    '!=': 3,
    '&&': 2,
    '||': 2,
    '!': 1,

    '=': 0,
    '+=': 0,
    '-=': 0,
    '*=': 0,
    '%=': 0,
    '/=': 0,
    '&=': 0,
    '|=': 0,
    '^=': 0,

    '.': 8,
    '(': -1,
}

symbols = {
    '(',
    ')',
    '[',
    ']',
    ',',
    ';',
    ':',
}

keywords = {
        "while", "for", "goto",
        "if", "else", "elif",
        "switch", "case", "default",
        "try", "catch", "finally",
        "class", "struct", "func", "namespace",

        "assert", "print", "input"
}

const_keywords = {
    'null': None, 'true': True, 'false': False
}

assignments = {
    '=',
    '+=',
    '-=',
    '*=',
    '%=',
    '/=',
    '&=',
    '|=',
    '^=',
}

def _get_op_codes():
    result = {}
    co = 0
    for first, seconds in operators.items():
        result[first] = co
        co += 1
        for second in seconds:
            result[first + second] = co
            co += 1
    return result
op_codes = _get_op_codes()

def _get_kw_codes():
    result = {}
    co = 0
    for k in keywords:
        result[k] = co
        co += 1
    return result
keyword_codes = _get_kw_codes()

def _get_symbol_codes():
    result = {}
    co = 0
    for sym in symbols:
        result[sym] = co
        co += 1
    return result
symbol_codes = _get_symbol_codes()


OpCode = namedtuple('OpCode', ['code', 'value'])


LOAD_REF       = 0
LOAD_VALUE     = 1
LOAD_CONST     = 2
CALL_FUNCTION  = 3
RETURN_VALUE   = 4
POP_TOP        = 5
BINARY_OP      = 6
UNARY_OP       = 7
JUMP_IF_TRUE   = 8
JUMP_IF_FALSE  = 9
JUMP_FORWARD   = 10
BUILD_LIST     = 11
PRINT_VALUE    = 12
INPUT_VALUE    = 13
LOAD_NAME      = 14
IMPORT_NAME    = 15
IMPORT_ALL     = 16


EXIT           = 100


class Code:
    def __init__(self, lexer, code):
        self.consts = lexer.consts
        self.identifiers = lexer.identifiers
        self.code = code


class Expr:
    def __init__(self, expr, lexer):
        self.expr = expr
        self.result = []
        self.lexer = lexer

    def compile(self):
        stack = []
        i = 0
        while i < len(self.expr):
            token = self.expr[i]
            if token.type == 'identifier':
                if self.expr.index(token) < len(self.expr) - 2 \
                        and self.expr[self.expr.index(token) + 1].value in assignments:
                    self.result.append(OpCode(LOAD_REF, token.code))

                elif self.expr.index(token) > 0 \
                        and self.expr[self.expr.index(token) - 1].value == '.':
                    self.result.append(OpCode(LOAD_NAME, token.code))

                else:
                    self.result.append(OpCode(LOAD_VALUE, token.code))
                if i < len(self.expr) - 1 and self.expr[i + 1].value == '(':
                    # 说明是函数调用
                    expr = []
                    args = []
                    i += 1
                    for t in self.expr[(i + 1):]:
                        i += 1
                        if t.value == ',':
                            args.append(Expr(expr, self.lexer))
                            expr = []
                            continue
                        if t.value == ')':
                            args.append(Expr(expr, self.lexer))
                            expr = []
                            break
                        expr.append(t)


                    for arg in args:
                        self.result.extend(arg.compile())
                    self.result.append(OpCode(CALL_FUNCTION, token.code))


            elif token.type == 'const':
                self.result.append(OpCode(LOAD_CONST, token.code))
            elif token.type == 'operator':
                if len(stack) == 0:
                    stack.append(token)
                else:
                    while len(stack) != 0 and op_priority[token.value] <= op_priority[stack[-1].value]:
                        self.result.append(OpCode(BINARY_OP, op_codes[stack.pop(-1).value]))
                    stack.append(token)
            elif token.type == 'symbol':
                if token.value == '(':
                    stack.append(token)
                elif token.value == ')':
                    while stack[-1].value != '(':
                        self.result.append(OpCode(BINARY_OP, op_codes[stack.pop(-1).value]))
                    stack.pop(-1)
            i += 1
        while len(stack) != 0:
            self.result.append(OpCode(BINARY_OP, op_codes[stack.pop(-1).value]))
        return self.result

    def __repr__(self):
        return str(self.expr)


class Stmt(ABC):
    """
    语句类的基类，需要子类继承并实现抽象方法
    """
    def __init__(self, lexer, stmt):
        """
        :param lexer: Lexer对象
        """
        self.stmt = stmt
        self.lexer = lexer

    def __repr__(self):
        return f'name={type(self).__name__} opcodes={self.compile()}'

    @abstractmethod
    def compile(self):
        """
        让语句对象执行编译操作
        :return: list[OpCode]
        """
        pass

class SimpleStmt(Stmt):
    """
    简单不带关键字的语句，即赋值/函数调用语句
    """

    def compile(self):
        """
         NAME assignment EXPR
        |NAME([EXPR0, [EXPR1, [...]]])
        """
        return Expr(self.stmt, self.lexer).compile()

class PrintValue(Stmt):
    def compile(self):
        """
         print EXPR
        """
        result = []
        result.extend(Expr(self.stmt[1:], self.lexer).compile())
        result.append(OpCode(PRINT_VALUE, -1))
        return result

class InputValue(Stmt):
    def compile(self):
        """
         input STRING NAME
        """
        return [
            OpCode(LOAD_CONST, self.stmt[1].code),
            OpCode(INPUT_VALUE, self.stmt[2].code)
        ]

class ImportModule(Stmt):
    def compile(self):
        """
         import PATH : (NAME,)* NAME
        |import PATH : *
        """
        if self.stmt[3].value == '*':
            return [OpCode(IMPORT_ALL, self.stmt[1].code)]
        else:
            names = filter(lambda e: e.value != ',', self.stmt[3:])
            return [OpCode(IMPORT_NAME, name.code) for name in names]

class IfStmt(Stmt):
    def compile(self):
        """
        if expr {code} (elif expr0 {code0})* [else {code1}]
        """
        Parser = __import__('Parser').parser.Parser
        have_else = self.stmt[-2].value == 'else'
        opcodes = [stmt.compile() for stmt in Parser(self.stmt[2].value).parse().stmt_objs]
        opcodes.extend(
            (stmt.compile()
                for co in filter(lambda e: e.type == 'code', self.stmt[3:-1])
                    for stmt in Parser(co.value).parse().stmt_objs)
            if have_else
            else
            (stmt.compile()
                for co in filter(lambda e: e.type == 'code', self.stmt[3:])
                    for stmt in Parser(co.value).parse().stmt_objs)
        )
        expressions = []
        flag = False
        expr = []
        for token in self.stmt:
            if token.type != 'code' and token.type != 'keyword':
                flag = True
            if flag:
                if token.type == 'code' or token.type == 'keyword':
                    expressions.append(Expr(expr, self.lexer))
                    expr = []
                    flag = False
                else:
                    expr.append(token)

        result = []
        for expr, codes in zip(expressions, opcodes):
            result.extend(expr.compile())
            result.append(OpCode(JUMP_IF_FALSE, len(codes) + 1))
            result.extend(codes)
        return result


statements = {
    'print': PrintValue,
    'import': ImportModule,
    'input': InputValue,
    'if': IfStmt,
}

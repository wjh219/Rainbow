from decimal import Decimal
from Parser.grammar import *

BreakLoop = type('BreakLoop', (Exception,), {})
ContinueLoop = type('ContinueLoop', (Exception,), {})


class Lexer:
    def __init__(self, text, lastl=None):
        self.consts: list = [None]
        self.identifiers: list = []
        self.pos = 0
        self.tokens = []
        self.lastl = lastl

        if text == '':
            self.tokens.append(EOF)
            return

        self.text = text + ' ' if text[-1] != ' ' else text
        self.char = text[self.pos]

        self.length = len(self.text)

    @staticmethod
    def is_letter(c: str):
        return ord('a') <= ord(c) <= ord('z') or \
            ord('A') <= ord(c) <= ord('Z')

    @classmethod
    def is_identifier(cls, c: str):
        return cls.is_letter(c) or c == '_'

    @staticmethod
    def is_number(c: str):
        return ord('0') <= ord(c) <= ord('9')

    @staticmethod
    def get_code(s):
        if s in op_codes.keys():
            return op_codes[s]
        elif s in symbol_codes.keys():
            return symbol_codes[s]
        elif s in keyword_codes.keys():
            return keyword_codes[s]

    @property
    def not_end(self): return len(self.tokens) == 0 or self.tokens[-1] != EOF  # 利用or的短路特性

    def next(self):
        self.pos += 1
        if self.pos >= self.length:
            self.tokens.append(EOF)
            return
        self.char = self.text[self.pos]

    def back(self):
        self.pos -= 1
        self.char = self.text[self.pos]

    def read_identifier(self):
        result = ''
        is_keyword = False
        is_const_kw = False

        while (self.is_identifier(self.char) or self.is_number(self.char)) and self.not_end:
            result += self.char
            is_keyword = result in keywords
            is_const_kw = result in const_keywords.keys()
            self.next()

        self.back()
        return result, is_keyword, is_const_kw

    def read_number(self):
        result = ''
        is_float = False

        while self.is_number(self.char) and self.not_end:
            result += self.char
            is_float = '.' in result
            self.next()

        self.back()
        return result, is_float

    def find_const(self, const):
        if self.lastl is None:
            try:
                return self.consts.index(const)
            except ValueError:
                self.consts.append(const)
                return len(self.consts) - 1

        else:
            return self.lastl.find_const(const)

    def find_identifier(self, iden):
        if self.lastl is None:
            try:
                return self.identifiers.index(iden)
            except ValueError:
                self.identifiers.append(iden)
                return len(self.identifiers) - 1
        else:
            return self.lastl.find_identifier(iden)

    def parse(self):
        while self.not_end:
            try:
                # 检测是否为运算符
                for first, seconds in operators.items():
                    if self.char == first:
                        self.next()
                        for second in seconds:
                            if self.char == second:
                                self.tokens.append(Token('operator', first + second, self.get_code(first + second)))
                                raise ContinueLoop
                        else:
                            self.tokens.append(Token('operator', first, self.get_code(first)))
                            self.back()
                            raise ContinueLoop

                # 检测是否为符号
                if self.char in symbols:
                    self.tokens.append(Token('symbol', self.char, -1))
                    raise ContinueLoop

                # 检测是否为空格 | 换行符
                elif self.char == '' or self.char == ' ' or self.char == '\n':
                    raise ContinueLoop

                # 检测是否为标识符或关键字
                elif self.is_identifier(self.char):
                    res, is_keyword, is_const_kw = self.read_identifier()
                    if is_keyword:
                        self.tokens.append(Token('keyword', res, self.get_code(res)))
                    elif is_const_kw:
                        const = const_keywords[res]
                        self.tokens.append(Token('const', const, self.find_const(const)))
                    else:
                        self.tokens.append(Token('identifier', res, self.find_identifier(res)))
                    raise ContinueLoop

                # 检测是否为常数
                elif self.is_number(self.char):
                    res, is_float = self.read_number()
                    number = Decimal(res) if is_float else int(res)
                    self.tokens.append(Token('const', number, self.find_const(number)))
                    raise ContinueLoop

                # 如果是字符串
                elif self.char == '\"' or self.char == '\'':
                    target = self.char
                    string = ''
                    self.next()
                    while self.char != target:
                        string += self.char
                        self.next()

                    self.tokens.append((Token('const', string, self.find_const(string))))
                    raise ContinueLoop

                # 如果是装饰器
                elif self.char == '@':
                    self.next()
                    iden, is_keyword, is_const_kw = self.read_identifier()
                    if is_keyword or is_const_kw:
                        raise

                    self.tokens.append(Token('decorator', iden, self.find_identifier(iden)))
                    raise ContinueLoop

                # 如果是大括号
                elif self.char == '{':
                    text = ''
                    count = 1
                    self.next()
                    while count > 0:
                        if self.char == '{':
                            count += 1
                        elif self.char == '}':
                            count -= 1
                        text += self.char
                        self.next()
                    text = '' if len(text) == 0 else (text[0:-1] if text[-1] == '}' else text)
                    lexer = Lexer(text, self)
                    lexer.parse()
                    self.tokens.append(Token('code', lexer, -1))
                    self.back()
                    raise ContinueLoop

                # 如果是未知字符
                else:
                    raise Exception(f'未知的字符\'{self.char}\'在{self.text}中')


            except ContinueLoop:
                self.next()


class Parser:
    def __init__(self, lexer):
        self.pos = 0
        self.lexer = lexer
        self.stmt_objs = []

    def parse(self):
        stmt = []
        i = 0
        while i < len(self.lexer.tokens):
            token = self.lexer.tokens[i]

            if token == Token('symbol', ';', -2):
                for t in stmt:
                    if t.value in statements.keys():
                        self.stmt_objs.append(statements[t.value](self.lexer, stmt))
                        break
                else:
                    self.stmt_objs.append(SimpleStmt(self.lexer, stmt))
                stmt = []
                i += 1
                continue

            stmt.append(token)
            i += 1
        else:
            if len(stmt) == 0:
                raise Exception("需要一个分号';'")
        return self

import sys
from decimal import Decimal
import os

sys.path.extend(['E:\\Codes\\RainbowScript', 'E:/Codes/RainbowScript'])

from Parser.parser import Lexer, Parser, OpCode
from sys import argv

if __name__ == '__main__':
    if len(argv) > 1:
        with open(argv[1], 'r') as file:
            text = file.read()

        lexer = Lexer(text)
        lexer.parse()
        parser = Parser(lexer)
        parser.parse()
        op_codes = []
        for stmt in parser.stmt_objs:
            op_codes.extend(stmt.compile())

        op_codes.append(OpCode(100, 100))

        """
        i: 接下来是个数字(chr)代表下来n位是标识符
        n: 接下来是两个数字表示 n * 1114111 + m
        f: 接下来是四个数字表示 (n1 * 1114111 + m1).(n2 * 1114111 + m2)
        s: 接下来是一个数字代表下来n位是字符串常量
        b: 接下来是一个字符 1:true, 0:false
        c: 表示接下来都是code
        """
        with open(os.path.splitext(argv[1])[0] + '.rbc', 'wb') as c_file:
            for identifier in lexer.identifiers:
                c_file.write(bytes('i' + chr(len(identifier)) + identifier, 'utf-8'))

            for const in lexer.consts:
                if type(const) == int:
                    digit = const // 1114111
                    num = const % 1114111
                    c_file.write(bytes('n' + chr(digit) + chr(num), 'utf-8'))

                elif type(const) == Decimal:
                    integer = const - round(const)
                    decimal = const - integer
                    digit1 = integer // 1114111
                    num1 = integer % 1114111
                    digit2 = decimal // 1114111
                    num2 = decimal % 1114111
                    c_file.write(bytes('f' +
                                       chr(digit1) + chr(num1) +
                                       chr(digit2) + chr(num2), 'utf-8'))

                elif type(const) == str:
                    c_file.write(bytes('s' + chr(len(const)) + const, 'utf-8'))

                elif type(const) == bool:
                    c_file.write(bytes('b' + ('1' if const else '0')))

                elif isinstance(const, type(None)):
                    pass

                else:
                    raise Exception()

            c_file.write(bytes('c', 'utf-8'))
            for code in op_codes:
                c_file.write(bytes(chr(100 if code[0] == -1 else code[0]) +
                                   chr(100 if code[1] == -1 else code[1]),
                                   'utf-8'))


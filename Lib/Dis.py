from Parser.grammar import op_codes
from Parser.parser import Parser
from itertools import chain
op_codes = {v: k for k, v in op_codes.items()}

opcodes = {
    0: ('LOAD_REF', 'i'),
    1: ('LOAD_VALUE', 'i'),
    2: ('LOAD_CONST', 'c'),
    3: ('CALL_FUNCTION', 'i'),
    4: ('RETURN_VALUE', 'n'),
    5: ('POP_TOP', 'n'),
    6: ('BINARY_OP', 'op'),
    7: ('UNARY_OP', 'uop'),
    8: ('JUMP_IF_TRUE', 'l'),
    9: ('JUMP_IF_FALSE', 'l'),
    10: ('JUMP_FORWARD', 'l'),
    11: ('BUILD_LIST', 'n'),
    12: ('PRINT_VALUE', 'n'),
    13: ('INPUT_VALUE', 'i'),
    14: ('LOAD_NAME', 'i'),
    15: ('IMPORT_NAME', 'c'),
    16: ('IMPORT_ALL', 'c'),
}

def dis(code: Parser):
    match = {
        'i': code.lexer.identifiers,
        'c': code.lexer.consts,
        'n': [None],
        'op': op_codes,
        'uop': op_codes,
    }
    codes = chain(*[stmt.compile() for stmt in code.parse().stmt_objs])
    for co in codes:
        line = f'{opcodes[co[0]][0]}{" " * 10}{co[1]}'
        if opcodes[co[0]][1] == 'l':
            line += f'(forward {co[1]})'
            print(line)
            continue
        line += f'({match[opcodes[co[0]][1]][co[1]]})'
        print(line)

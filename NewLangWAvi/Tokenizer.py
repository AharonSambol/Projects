import re

from Tokens import *


def tokenize(input_code):
    res = []
    bracket_types = []
    cur_token = ''
    is_num_dig = re.compile(r'\w')
    in_comment = False
    in_str = False
    is_escaped = False
    for i, c in enumerate(input_code):
        if in_str:
            if c == in_str and not is_escaped:
                in_str = False
                res.append(Token(Tokens.STR_CONSTANT, cur_token))
                cur_token = ''
            else:
                cur_token += c
                if is_escaped:
                    is_escaped = False
                elif c == '\\':
                    is_escaped = True
            continue

        if c == '\t':
            continue
        if in_comment:
            if c == in_comment == '\n':
                in_comment = False
            elif c == in_comment == '`' == input_code[i - 1]:
                in_comment = False
                continue
            else:
                continue
        if cur_token == '`':
            in_comment = '`' if c == '`' else '\n'
            cur_token = ''
            continue
        if c in ['"', "'"]:
            cur_token = eat_token(cur_token, res, bracket_types)
            in_str = c
            continue
        prev = cur_token[-1] if cur_token else ''
        if c in '[](){}:':
            cur_token = eat_token(cur_token, res, bracket_types)
            eat_token(c, res, bracket_types)
            continue
        if c in [' ', '\n']:
            if cur_token != '#':
                cur_token = eat_token(cur_token, res, bracket_types)
            if c == '\n':
                res.append(Token(Tokens.NEW_LINE, '\n'))
        elif c == '~':
            cur_token = eat_token(cur_token, res, bracket_types)
            eat_token('~', res, bracket_types)
        else:
            if not prev:
                cur_token = c
            else:
                if cur_token == '#' or bool(is_num_dig.match(c)) == bool(is_num_dig.match(prev)):
                    cur_token += c
                else:
                    eat_token(cur_token, res, bracket_types)
                    cur_token = c
            if c == ',':
                cur_token = eat_token(cur_token, res, bracket_types)
    eat_token(cur_token, res, bracket_types)
    res = comprehension_vs_literal(res)
    res = subtracting_vs_negative(res)
    res = dict_vs_program(res)
    res = bigger_smaller_vs_generic(res)
    return res


def eat_token(cur_token, res, bracket_types):
    if cur_token.strip():
        tok = determine_token(cur_token, res, bracket_types)
        if tok:
            res.append(tok)
    return ''


def comprehension_vs_literal(res):
    types = []
    for i, tok in enumerate(res):
        if tok.type is None:
            if tok.name == ']':
                if not types:
                    raise Exception("Too many closing brackets")
                res[i] = Token(types.pop(), ']')
            else:
                amount_open = 1
                pos = i + 1
                is_comprehension = False
                while amount_open:
                    if res[pos].type is None:
                        amount_open += {'[': 1, ']': -1}[res[pos].name]
                    elif res[pos].type == Tokens.LOOP:
                        is_comprehension = True
                        break
                    pos += 1
                if is_comprehension:
                    res[i] = Token(Tokens.LIST_COMPREHENSION, '[')
                else:
                    res[i] = Token(Tokens.LIST, '[')
                types.append(res[i].type)
    return res


def subtracting_vs_negative(prev_res):
    res = []
    for i, tok in enumerate(prev_res):
        if tok.name == '-':
            if not res or (
                    res[-1].type not in [Tokens.INT_CONSTANT, Tokens.OTHER, Tokens.FLOAT_CONSTANT]
                    and res[-1].name not in [')', ']']):
                res.append(Token(Tokens.NEGATIVE, '-'))
                continue
        res.append(tok)
    return res


def bigger_smaller_vs_generic(prev_res):
    res = []
    is_generic = ''
    for i, tok in enumerate(prev_res):
        if tok.name == '<':
            if (i + 2 < len(prev_res) and
                    prev_res[i + 1].type == Tokens.OTHER and prev_res[i + 2].name == '>'):
                is_generic = '<'
                continue
        if is_generic and tok.name == '>':
            res[-1] = Token(res[-1].type, res[-1].name + is_generic + '>')
            is_generic = ''
            continue
        if is_generic:
            if is_generic != '<':
                raise Exception(f"Can only have one thing inside Generic brackets, not { is_generic + tok.name }")
            is_generic += tok.name
            continue
        res.append(tok)
    return res


def dict_vs_program(prev_res):
    res = []
    is_dict = lambda i: (prev_res[i + 1].type == prev_res[i + 3].type == Tokens.OTHER
                         and prev_res[i + 2].type == Tokens.COMMA
                         and prev_res[i + 4].type == Tokens.COLON)
    is_set = lambda i: (prev_res[i + 1].type == Tokens.OTHER
                        and prev_res[i + 2].type == Tokens.COLON)
    for i, tok in enumerate(prev_res):
        if tok.name == '{':
            if is_set(i) or is_dict(i):
                typ = Tokens.SET if is_set(i) else Tokens.DICT
                res.append(Token(typ, '{'))
                open_ = 1
                pos = i + 5
                while open_:
                    if prev_res[pos].name == '}':
                        open_ -= 1
                        if open_ == 0:
                            prev_res[pos] = Token(typ, '}')
                    elif prev_res[pos].name == '{':
                        open_ += 1
                    pos += 1
                continue
        res.append(tok)
    return res


single_option_tokens = {
    'null': Tokens.NULL_CONSTANT,
    '-?': Tokens.REMOVE_NULL,
    'for': Tokens.LOOP,
    'index': Tokens.INDEX_KEYWORD,
    ',': Tokens.COMMA,
    '.': Tokens.DOT,
    '..': Tokens.DOT_DOT,
    '=?': Tokens.SHORT_SHORT_IF,
    '??': Tokens.SHORT_NULL_IF,
    '=??': Tokens.SHORT_SHORT_NULL_IF,
    '?': Tokens.QUESTION_MARK,
    ':': Tokens.COLON,
    # 'switch': Tokens.SWITCH,
    # '->': Tokens.CASE,
    # '<-': Tokens.SWITCH_RETURN,
    'override': Tokens.OVERRIDE,
    'const': Tokens.CONST,  # 3 maybe dont need?
    'raise': Tokens.THROW,
    '|': Tokens.PIPE,
    '~': Tokens.CLASS_PARTS,
    '!': Tokens.EXCLAMATION_MARK,
    '$': Tokens.DOLLAR,
}


def determine_token(st, res, bracket_types):
    if tok := single_option_tokens.get(st, False):
        return Token(tok, st)
    if st == 'in':
        if res and res[-1].name == 'not':
            res.pop()
            return Token(Tokens.BOOL_OPERATOR, 'not in')
        return Token(Tokens.IN, 'in')
    if st in ['true', 'false']:
        return Token(Tokens.BOOL_CONSTANT, st)
    if st in ['++', '--']:
        return Token(Tokens.PLUS_PLUS, st)  # todo before var, eg: (x = ++y)
    if st in ['+', '-', '/', '/-/', '/+/', '*', '^', '%']:
        return Token(Tokens.MATH_OPERATOR, st)
    if st in ['==', '!=', '>=', '>', '<=', '<', 'not', 'and', 'or', 'xor', 'nand']:
        return Token(Tokens.BOOL_OPERATOR, st)
    if st in ['(', ')']:
        return Token(Tokens.PARENTHESES, st)
    if st in ['{', '}']:
        return Token(Tokens.BRACES, st)
    if st in ['if', 'else', 'until', 'while', 'unless', 'elif', 'loop', 'switch', 'case']:
        return Token(Tokens.CONDITION, st)
    if st in ['break', 'continue', 'rewind', 'restart', 'return']:
        return Token(Tokens.CONTROL_MODIFIER, st)
    if st in ['@', '$', ';']:
        return Token(Tokens.SPECIAL_CHAR, st)
    if st in ['Obj', 'Struct', 'Type', 'Instructions', 'StaticObj', 'Record']:
        return Token(Tokens.CLASS_TYPE, st)
    if st in ['extends', 'implements', 'vars', 'staticVars', 'funcs', 'staticFuncs']:
        # todo make these 'static vars' instead of 'staticVars'
        return Token(Tokens.CLASS_PARTS, st)
    if st in ['get', 'set']:
        return Token(Tokens.GET_SET, st)
    if st in ['try', 'fix', 'finally']:
        return Token(Tokens.TRY_CATCH_FINALLY, st)
    if st[0] == '#':
        return Token(Tokens.TAG, st[1:].strip())
    if st == '[':
        if res:
            prev = res[-1]
            if (prev.type == Tokens.OTHER or
                    (prev.type == Tokens.PARENTHESES and prev.name == ')') or
                    prev.type == Tokens.INDEX):
                bracket_types.append(Tokens.INDEX)
                return Token(Tokens.INDEX, '[')
            bracket_types.append(None)
            return Token(None, '[')  # 3 if contains 'for' its comprehension else literal
    if st == ']':
        if bracket_types[-1] == Tokens.INDEX:
            if res[-1].name == '[':
                res.pop()
                bracket_types.pop()
                res[-1] = Token(res[-1].type, res[-1].name + '[]')
                return False
        return Token(bracket_types.pop(), ']')
    if len(st) > 1:
        if st[0] == st[-1] == '"':
            return Token(Tokens.STR_CONSTANT, st)
        if st[0] == st[-1] == '-':
            return Token(Tokens.OTHER, st)
    if re.fullmatch(r'(\+|-|\*|\\|\\{2}|%|\^)?=', st):
        return Token(Tokens.ASSIGNMENT, st)
    if re.fullmatch(r'\d+', st):
        if len(res) > 1:
            if res[-1].type == Tokens.DOT and res[-2].type == Tokens.INT_CONSTANT:
                st = f'{ res[-2].name }.{ st }'
                res.pop()
                res.pop()
                return Token(Tokens.FLOAT_CONSTANT, st)
        return Token(Tokens.INT_CONSTANT, st)
    if re.fullmatch(r'\d+\.\d+', st):
        return Token(Tokens.FLOAT_CONSTANT, st)
    if re.fullmatch(r'[a-zA-Z_]\w*', st):
        return Token(Tokens.OTHER, st)
    raise Exception(f"Unknown token: {st}")
    # todo cast
    # todo indexing
    # todo list constant
    # todo list comprehension

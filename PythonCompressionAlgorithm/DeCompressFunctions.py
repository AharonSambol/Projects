import re

EXCEPTIONS = {'Exception': '&0', 'AssertionError': '&1', 'AttributeError': '&2', 'ArithmeticError': '&3',
              'EOFError': '&4', 'FloatingPointError': '&5', 'GeneratorExit': '&6', 'ImportError': '&7',
              'IndentationError': '&8', 'IndexError': '&9', 'KeyError': '&a', 'KeyboardInterrupt': '&b',
              'LookupError': '&c', 'MemoryError': '&d', 'NameError': '&e', 'NotImplementedError': '&f', 'OSError': '&g',
              'OverflowError': '&h', 'ReferenceError': '&i', 'RuntimeError': '&j', 'StopIteration': '&k',
              'SyntaxError': '&l', 'TabError': '&m', 'SystemError': '&n', 'SystemExit': '&o', 'TypeError': '&p',
              'UnboundLocalError': '&q', 'UnicodeError': '&r', 'UnicodeEncodeError': '&s', 'UnicodeDecodeError': '&t',
              'UnicodeTranslateError': '&u', 'ValueError': '&v', 'ZeroDivisionError': '&w', 'RecursionError': '&x',
              'ModuleNotFoundError': '&y'}
ABBREVIATIONS = {'and': 'a', 'or': 'o', 'is': 'i', 'not': 'n', 'in': 'I', 'None': 'N', 'True': 'T', 'False': 'F'}
KEYWORDS = {'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'False',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or',
            'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'}

INDENT_KEYWORDS = ['if', 'else', 'elif', 'while', 'for', 'def', 'class', 'try', 'except', 'with', 'finally',
                   'async def', 'async for', 'async with']
OPEN_BRACKETS = ['{', '(', '[']
CLOSE_BRACKETS = ['}', ')', ']']

exceptions_rvrs = {v: k for k, v in EXCEPTIONS.items()}
abbreviations_rvrs = {v: k for k, v in ABBREVIATIONS.items()}

is_num = lambda x: x[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


def ungroup_nums(line):
    while ',,' in line:
        for c, char in enumerate(line):
            if c+1 < len(line) and line[c+1] == char == ',':
                if c+2 < len(line) and line[c+2] == ',':
                    c += 1
                end = c + 2
                while end < len(line) and (line[end].isdigit() or line[end] == '_'):
                    end += 1
                line = line[:c] + ','.join(list(line[c+2:end].replace('_', ''))) + line[end:]
                break
    return line


def snake(word):
    start, end = word.group(1), word.group(3)
    if re.match(r'\w', start):
        start += ' '
    if re.match(r'\w', end):
        end = ' ' + end
    word = word.group(2)
    num = ''
    while word[0].isdigit():
        num += word[0]
        word = word[1:]
    new_word = ''
    for c in word:
        if c.isupper():
            new_word += '_'
            c = c.lower()
        new_word += c
    if num != '':
        dashes = '_' * int(num)
        new_word = dashes + new_word + dashes

    return start + new_word + end


def to_snake_case(line):
    line = re.sub(r'(.?)`(\w+)`(.?)', snake, line)  # twice in case there are 2 next to each other
    return re.sub(r'(.?)`(\w+)`(.?)', snake, line)


def close_brackets(line):
    opposites = {'{': '}', '(': ')', '[': ']', '}': '{', ')': '(', ']': '['}
    stack = []
    for c in line:
        if c in OPEN_BRACKETS:
            stack.append(c)
        elif c in CLOSE_BRACKETS:
            if opposites[c] != stack.pop(-1):
                raise Exception("BAD BRACKETS?!?")
    for c in stack[::-1]:
        line += opposites[c]
    return line


def init_param(file, line, i):
    orig = get_param(line)
    if orig == ['']:
        return line
    param = [x for x in orig]
    for p, par in enumerate(param):
        if par == '':
            # cuz of how black formats -
            # def __init__(self, form, fieldsets, prepopulated_fields, readonly_fields=None, model_admin=None):
            continue
        if par[0] == '+':
            param[p] = par[1:]
            file.insert(i + 1, f'self.{param[p]} = {param[p]}')
    return line.replace(','.join(orig), ', '.join(param))


def get_param(line):
    while line[0] != '(':
        line = line[1:]
    line = line[1:-1]
    res = ['']
    amount_open = 0
    for c in line:
        if c == ',' and amount_open == 0:
            res.append('')
        else:
            amount_open += count_brackets_single(c)
            res[-1] += c
    return res


def put_back_self(line, is_def):
    if is_def:
        line = line.replace('(,', '(self,').replace(',,', ', self,')
    else:
        line = re.sub(r'((?<=[^\w}\])!\'".])|^)\.(?!\.)', 'self.', line)
    return line


def get_before_comment(line):
    if '#' not in line:
        return line
    ignore_next, in_str = 0, False
    for c, char in enumerate(line):
        if ignore_next:
            ignore_next -= 1
            continue
        if char in ['"', "'"]:
            if char == in_str:
                if c > 0 and c + 1 < len(line) and line[c - 1] == line[c + 1] == char:
                    # multiline str
                    ignore_next = 2
                    in_str *= 3
                else:
                    in_str = False
            elif char * 3 == in_str:
                if c + 2 < len(line) and char == line[c + 1] == line[c + 2]:
                    in_str = False
                    ignore_next = 2
            elif not in_str:
                in_str = char
        elif char == '\\':
            ignore_next = 1
        elif char == '#' and not in_str:
            return line[:c]
    return line


def put_back(file, put_from, symbol, is_lossy):
    i = 0
    to_pop = []
    mn_pos = (-1, -1)
    for st in put_from:
        for line_num in range(i, len(file)):
            line = file[line_num]
            start = mn_pos[1] if mn_pos[0] == line_num else 0
            if symbol in line[start:]:
                to_rep = '' if is_lossy else st
                symbol_indx = line.index(symbol, start)
                if symbol_indx >= len(get_before_comment(line)):
                    continue
                mn_pos = (line_num, symbol_indx + len(to_rep))
                if symbol_indx-2 >= 0 and line[symbol_indx-2:symbol_indx] in ['""', "''"]:
                    to_rep = ' ' + to_rep
                if symbol_indx+len(symbol) + 2 < len(line) and line[symbol_indx+len(symbol):symbol_indx+len(symbol) + 2] in ['""', "''"]:
                    to_rep += ' '
                file[line_num] = line = line[:symbol_indx] + to_rep + line[symbol_indx + len(symbol):]
                if line.strip() == '':
                    to_pop.append(line_num)
                i = line_num
                break
    for i in to_pop[::-1]:
        file.pop(i)


def remove_strings(file):
    strings, string_positions = [], []
    in_str = ignore_next = False
    start = (-1, -1)
    in_multiline_comment = False    # 5 !!!!!!!!!!!!!! only works for multiline comments that start at start of line
    for i, line in enumerate(file):
        valid_line = line
        while len(valid_line) > 0 and valid_line[0] in ['}', ' ', '\t']:
            valid_line = valid_line[1:]
        if not in_str and valid_line.startswith('$') or valid_line.startswith('!$'):
            in_multiline_comment = not in_multiline_comment
            continue
        if in_multiline_comment:
            continue
        ignore_next, in_str, start = find_string_positions(i, ignore_next, in_str, line, start, string_positions)
    remove_strings_given_positions(file, string_positions, strings)
    return strings


def find_string_positions(i, ignore_next, in_str, line, start, string_positions):
    for c, char in enumerate(line):
        if ignore_next:
            ignore_next -= 1
            continue
        if char in ['"', "'"]:
            if char == in_str:
                if start[0] == i and start[1] == c - 1 and c + 1 < len(line) and line[c + 1] == char:
                    # multiline str
                    ignore_next = 1
                    in_str *= 3
                else:
                    string_positions.append((start, (i, c)))
                    in_str = False
            elif char * 3 == in_str:
                if c + 2 < len(line) and char == line[c + 1] == line[c + 2]:
                    string_positions.append((start, (i, c + 2)))
                    in_str = False
                    ignore_next = 2
            elif not in_str:
                start, in_str = (i, c), char
        elif char == '\\':
            ignore_next = 1
        elif char == '#' and not in_str:
            break
    return ignore_next, in_str, start


def remove_strings_given_positions(file, string_positions, strings):
    for start, end in string_positions:
        if start[0] == end[0]:
            st = file[start[0]][start[1]: end[1] + 1]
            strings.append(st)
        else:
            st = file[start[0]][start[1]:] + '\n'
            for i in range(start[0] + 1, end[0]):
                st += file[i] + '\n'
            strings.append(st + file[end[0]][:end[1] + 1])
    for start, end in string_positions[::-1]:
        if start[0] == end[0]:
            line = file[start[0]]
            file[start[0]] = line[:start[1]] + '!str!' + line[end[1] + 1:]
        else:
            file[start[0]] = file[start[0]][:start[1]] + '!str!' + file[end[0]][end[1] + 1:]
            for i in range(start[0], end[0]):
                file.pop(start[0] + 1)


def remove_comments(file, strings):
    comments = []
    in_multiline = actually_unparseable_code = False
    for l, line in enumerate(file):
        start = ''
        comment_pos = line.index('#') if '#' in line else len(line)
        dollar_pos = line.index('$') if '$' in line else len(line)
        if not in_multiline and dollar_pos < comment_pos:
            actually_unparseable_code = dollar_pos != len(line) and line[max(0, dollar_pos-1)] == '!'
            in_multiline = l
            if actually_unparseable_code:
                start, line = line[:max(dollar_pos-1, 0)], line[dollar_pos+1:]
            else:
                start, line = line[:dollar_pos], line[dollar_pos + 1:]
            file[l] = start + line  # is necessary??

        if len(line) == 0:
            if in_multiline:
                comments.append('')
                file[l] = '!comment!'
            continue
        if in_multiline:
            if in_multiline != l and line[0] == '$':
                in_multiline = False
                file[l] = line = line[1:]
            if actually_unparseable_code:
                line = line.strip()
                if '!str!' in line:
                    line = restore_specific_str(file, line, l, strings)
                comments.append(line.strip())
            else:
                comments.append('# ' + line.strip())
            file[l] = start + '!comment!'
            continue
        if '#' in line:
            pos = line.index('#')
            comments.append('# ' + line[pos + 1:].strip())
            file[l] = line[:pos] + '!comment!'
    return comments


def restore_specific_str(file, line_this, l, strings):
    count = 0
    for line in file[:l]:
        count += line.count('!str!')
    while '!str!' in line_this:
        file[l] = line_this = line_this.replace('!str!', strings.pop(count), 1)
    return line_this


def to_correct_case(line):
    if '`' in line:
        return to_snake_case(line)
    return line


def replace_imports(file):
    i = 0
    import_re = re.compile(r'([^\s]+>|=?[^\s=]+)')
    while file[i].strip() != '%':
        file[i] = to_correct_case(file[i])
        groups = import_re.findall(file[i])
        new_line = 'import '
        last_is_import = True
        for group in groups:
            if group == '!comment!':
                if len(new_line) > 0 and new_line[-1] == ',':
                    new_line = new_line[:-1]
                new_line += group
            elif group[-1] == '>':
                new_line = f'from { group[:-1] } import '
            elif group[0] == '=':
                new_line += f' as { group[1:] }'
            else:
                new_line += ('' if last_is_import else ', ') + group
                last_is_import = False
        file[i] = new_line
        i += 1
    file[i] = ''
    return i


def split_raise_except(line):
    parts = [line[0], '', '']
    line = line[1:]
    if not line.startswith('!str!'):
        line = line[1:]

    amount_open = 0
    line = line.strip()
    while len(line) > 0 and (re.match(r'[^\s]', line[0]) or amount_open > 0):
        amount_open += count_brackets_single(line[0])
        if line[0] in ['<', '='] and amount_open == 0:
            break
        parts[1] += line[0]     # can optimize to use indexes instead of constantly popping
        line = line[1:]
    parts[2] = line.strip()[len('<'):]
    return [x.strip() for x in parts]


def decompress_exception_raise(line):
    # parts = re.match(r'([et])!(?:(str!|\w[^\s]*(?:\([^\s<]+\))?)?(?:(?:<)([^\s]+))?)', line).groups()
    parts = split_raise_except(line)
    res = 'except' if parts[0] == 'e' else 'raise'
    if parts[1] == '':
        return res
    res += ' ' + get_exception(parts[1])
    if parts[2] != '':
        res += (' from ' if parts[0] == 't' else ' as ') + get_exception(parts[2])
    return res


def get_exception(st):
    if st[0] == '&':
        return exceptions_rvrs[st]
    # if st in ['!str!', 'str!']:
    #     return 'Exception(!str!)'
    return st


def get_vars(line):
    # left_bound = r'(?:(?<=[^\w])|^)'
    # right_bound = r'(?:(?=[^\w\(\.])|$)'
    left_bound = r'(?:\b|^)'
    right_bound = r'(?:\b|$)'
    word = r'[a-zA-Z_]\w*'
    regex = left_bound + word + right_bound
    if line[:2] in ['f!', 'e!', 't!']:
        line = line[2:]
    parts = re.findall(regex, line.replace('!str!', ' ').replace('!comment!', ' '))
    res = list(filter(lambda x: x not in KEYWORDS, parts))
    return res


def default_for_functions(line):
    return [line]


def replace_following(line, following_checks_re):
    new_line = line
    for abrv in following_checks_re.findall(line):
        new_abrv = ' '.join(abbreviations_rvrs[x] for x in abrv if x != '@')
        new_line = new_line.replace(abrv, new_abrv, 1)
    return new_line


def restore_num(num, changed):
    res, is_dec = '', True
    if len(num) > 1 and num[0] == '0' and num[1] in ['b', 'e', 'o', 'x']:
        return num, False
        # res = num[:2]
        # num = num[2:]
        # is_dec = False
    for dig in num:
        if dig.isnumeric() or dig == '.' or ord(dig) > 90 or ord(dig) < 65:
            res += dig
        else:
            res += '0' * (ord(dig) - 64)
    # if is_dec:
    #     res = '_'.join(re.findall(r"[\d.]{1,3}(?=(?:\d{3})*$)", res))
    return res, changed or res != num


def restore_nums(line):
    parts = re.findall(r'((?<!\w)(?:\d[\w.]*)|.)', line)
    changed = False
    for v, val in enumerate(parts):
        if len(val) > 1:
            parts[v], changed = restore_num(val, changed)
    return ''.join(parts) if changed else line


def starts_with_indent_keyword(line):
    for indent_cmd in INDENT_KEYWORDS:
        if re.search('^' + indent_cmd + r'\b', line):
            return indent_cmd
    return None


def get_judge_by(judge_by, comments, comment_count, with_remove=True):

    if judge_by == '!comment!':
        comment = comments[comment_count]
        if len(comment) > 0 and comment[0] != '#':
            judge_by = comment
            if with_remove:
                if judge_by[0] == '!':
                    judge_by = judge_by[1:]
                judge_by = judge_by[1:]
    return judge_by


def indent(indentation, line, comments, comment_count):
    to_indent = indentation
    judge_by = get_judge_by(line, comments, comment_count)
    indent_word = starts_with_indent_keyword(judge_by)
    if indent_word is not None:
        if indent_word in ['elif', 'else', 'except', 'finally']:
            to_indent -= 1
        else:
            indentation += 1
        line += ':'
    line = '    ' * to_indent + line
    return line, indentation


def count_brackets(line):
    amount_of_open = 0
    for bracket in OPEN_BRACKETS:
        amount_of_open += line.count(bracket)
    for bracket in CLOSE_BRACKETS:
        amount_of_open -= line.count(bracket)
    return amount_of_open


def count_brackets_single(char):
    return {'[': 1, '{': 1, '(': 1, ']': -1, '}': -1, ')': -1}.get(char, 0)

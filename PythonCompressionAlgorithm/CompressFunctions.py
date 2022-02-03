from CheckResults import *
from Decompress import EXCEPTIONS, ABBREVIATIONS, INDENT_KEYWORDS
from Decompress import get_vars, is_num
from Decompress import get_param, restore_specific_str
from Decompress import OPEN_BRACKETS, CLOSE_BRACKETS
from Decompress import get_judge_by, starts_with_indent_keyword
from DeCompressFunctions import remove_strings_given_positions, find_string_positions
from DeCompressFunctions import count_brackets, count_brackets_single, to_correct_case
from DeCompressFunctions import BUILT_IN_FUNCTIONS, ALPHABET
from ReplaceSymbols import *

start_of_re = r'(?:^|(?<!\d))'  # not a number
end_of_re = r'(?:\d(?:$|(?!\d)))?'  # maybe a number
digits_and_commas_re = re.compile('(' + start_of_re + r'(?:\d,)+' + end_of_re + ')')


# todo also replace imports not at head of file
def replace_imports(input_file, start=0):
    import_re = re.compile(r'(from\b ?[^\s]+\b ?)?import\b ?((, ?)?[^\s,]+( as [^\s]+)?)+')
    i = start - 1
    for i, line in enumerate(input_file[start:] + ['']):
        amount_of_close, line = count_close_brackets(line)

        line = to_correct_case(line)
        if not import_re.match(line):
            break
        # line = list(import_re.match(line).groups())
        ends_with_comment = line.endswith(COMMENT)
        if ends_with_comment:
            line = line[:-COMMENT_LEN].strip()

        line = [x for x in re.split(r'[\s,]+', ' '.join(re.split(r'\b', line.strip()))) if x.strip() != '']

        # not_seperator = lambda x: x.strip(' ,') not in ['', 'import']
        # line = [x.replace(',', '') for x in re.split(r'\b', line.strip()) if not_seperator(x)]
        new_line = ''
        if line[0] == 'from':
            line.pop(0)
            new_line += line.pop(0) + FROM
        while line[0] != 'import':
            new_line = new_line[:-1] + line.pop(0) + FROM
        line.pop(0)
        new_line += line.pop(0)
        for nxt in line:
            if nxt == 'as':
                new_line += AS
            else:
                new_line += ('' if new_line[-1] in ['=', '(', '.'] or nxt == '.' else ' ') + nxt
        input_file[start + i] = CLOSE_INDENT * amount_of_close + new_line.strip()
        input_file[start + i] += COMMENT if ends_with_comment else ''

    if start + i < len(input_file) and not input_file[start + i].startswith(STR):
        input_file.insert(start + i, END_IMPORTS)
    return start + i


def shorten_for_common_usses(line):
    if re.search(r'for \w+ in range\(', line):
        line = re.sub(r'\bfor _ in range\(', FOR_IN_RANGE, line)
        line = re.sub(r'\bfor (\w+) in range\(', FOR_IN_RANGE_NAME + r'\1(', line)
    if re.search(r'\b(\w+) for \1 in', line):
        line = re.sub(r'\b(\w+) for \1 in', COMPREHENSION_RANGE + r'\1', line)
    return line


def count_close_brackets(line):
    amount_of_close = 0
    while len(line) > 0 and line[0] == CLOSE_INDENT:
        line = line[1:]
        amount_of_close += 1
    return amount_of_close, line


def remove_strings(file):
    strings, string_positions = [], []
    in_str = ignore_next = False
    start = (-1, -1)
    for i, line in enumerate(file):
        ignore_next, in_str, start = find_string_positions(i, ignore_next, in_str, line, start, string_positions)
    remove_strings_given_positions(file, string_positions, strings)
    return strings


def contains_dict(line):
    open_brackets = 0
    dict_layer = [-10]
    for char in line:
        if char in OPEN_BRACKETS:
            open_brackets += 1
            if char == '{':
                dict_layer.append(open_brackets)
        elif char in CLOSE_BRACKETS:
            if dict_layer[-1] == open_brackets:
                dict_layer.pop(-1)
            open_brackets -= 1
        elif char == ':' and dict_layer[-1] == open_brackets:
            return True
    return False


def group_nums(line):
    line = line.group(1)
    if line.strip(',').count(',') <= 2:
        return line
    end = ',' if line[-1] == ',' else ''
    line = line.replace(',', '')
    return GROUPED_NUMS + line + end


def numbers_with_commas(line):
    return digits_and_commas_re.sub(group_nums, line)


def replace_common_words(line):
    if 'self' in line:
        line = remove_self(line)
    if ' or ' in line:
        line = line.replace(' or ', OR)
    if ' and ' in line:
        line = line.replace(' and ', AND)
    if ' not ' in line:
        line = line.replace(' not ', NOT)
    if ' is ' in line:
        line = line.replace(' is ', IS)
    if ' __init__ ' in line:
        line = line.replace(' __init__ ', INIT)
    if ' True ' in line:
        line = line.replace(' True ', TRUE)
    if ' False ' in line:
        line = line.replace(' False ', FALSE)
    return line


def to_camel_case(file):
    upper = lambda match: match.group(1).upper()
    for l, line in enumerate(file):
        words = re.findall(r'(\s+|\.|,|[^\s.,]+)', line)
        changed = False
        for i, word in enumerate(words):
            if re.match(r'(\s+|\.|,)', word):
                continue
            if word.islower() and re.fullmatch(r'\w+', word):
                surrounding = 0
                while word[0] == word[-1] == '_':
                    word = word[1:-1]
                    surrounding += 1
                amount_dashes = len(re.split(r'_([a-zA-Z])', word)) - 1
                if amount_dashes > 2 or amount_dashes + surrounding > 2:
                    surrounding = str(surrounding) if surrounding != 0 else ''
                    words[i] = CAMEL_CASE + surrounding + re.sub(r'_([a-zA-Z])', upper, word) + CAMEL_CASE
                    changed = True
        if changed:
            file[l] = ''.join(words)


def replace_functions(line, functions):
    to_rep = []
    for c, char in enumerate(line):
        if char == '(':
            pos, name = 1, ''
            while c - pos >= 0 and re.match(r'\w', line[c - pos]):
                name = line[c - pos] + name
                pos += 1
            if name in functions:
                to_rep.append((c - pos + 1, c, functions[name]))

    for start, end, name in to_rep[::-1]:
        line = line[:start] + name + line[end:]
    return line


def init(file, line, i):
    # check for double assignment x, y = 1, 2 or x = y = 5
    params = get_param(line)
    assigned_param = []
    i += 1
    while True:
        for param in params:
            if i < len(file) and file[i] == f'self.{param}={param}':
                file.pop(i)
                assigned_param.append(param)
                break
        else:
            break
    res = ''
    for p, param in enumerate(params):
        if param in assigned_param:
            res += INITED  # TODO probably don't need a , before an INITED
        res += param + (',' if p + 1 != len(params) else '')
    line = line.replace(','.join(params), res)
    return line


def get_function(file, orig_line_num):
    line_num = orig_line_num + 1
    indent = 1
    while line_num < len(file):
        cls = count_close(file[line_num])
        indent -= cls
        if indent <= 0:
            break
        # def and class?

        for indenter in INDENT_KEYWORDS:
            if file[line_num][cls:].startswith(indenter):
                indent += 1
                break
        line_num += 1
    return file[orig_line_num: line_num]


def count_close(line):
    res = 0
    while line[res] == CLOSE_INDENT:
        res += 1
    return res


def is_valid_self(line, start, end):
    if start != 0 and re.match(r'[\w\]})\'"]', line[start - 1]):
        return False
    if end + 1 >= len(line) or re.match(r'\w', line[end + 1]):
        return False
    if line.startswith(DEF) and line[end + 1] == ',':
        return True
    if line[end + 1] == '.':
        return True
    return False


def find_indexes_self(line):
    pattern = 'self'
    pat_indx, res, ignore_next = 0, [], False
    for i, c in enumerate(line):
        if ignore_next:
            ignore_next = False
            continue
        if c == pattern[pat_indx]:
            pat_indx += 1
            if pat_indx == len(pattern):
                pat_indx = 0
                start, end = i - len(pattern) + 1, i
                if is_valid_self(line, start, end):
                    res.append((start, end))
        else:
            pat_indx = 0
            if re.match(r'\w', c):
                ignore_next = True
    return res


def remove_self(line):
    indexs = find_indexes_self(line)
    for start, end in indexs[::-1]:
        line = line[:start] + line[end + 1:]
    return line
    # return re.sub(r'((?<=[^\w])|^)self((?=[^\w])|$)', '', line)


def compress_while(line):
    if line == 'while True':
        return WHILE
    return WHILE + line[len('while'):].strip()


# todo add more
def compress_if(line):
    return IF + line[len('if'):].strip()


def split_for(line):
    line = line[len('for'):]
    open_brackets = 0
    names = ''
    for c, char in enumerate(line):
        open_brackets += count_brackets_single(char)
        if open_brackets == 0 and re.match(r'.\bin\b.', line[c - 1:c + 3]):
            names = line[:c]
            break
    return [names.strip(), line[len(names) + 2:].strip()]


def compress_for(file, line, line_num):
    # try:
    #     parts = re.match(r'for\b(.+?)\bin\b\s*(.+)', line).groups()
    # except Exception:
    #     raise Exception from Exception
    parts = split_for(line)
    var_names = parts[0].strip().split(',')
    for i, var in enumerate(var_names):
        var_names[i] = get_num_var(file, var, line_num)
    vars = ''
    last_was_num = True
    for vr in var_names:
        if not last_was_num or (vars != '' and not is_num(vr)):
            vars += ','
        last_was_num = is_num(vr)
        vars += vr
    iters = default_for_functions(parts[1])
    line = FOR + vars + IN + iters
    return line


def get_num_var(file, var, line_num):
    res, seen = -1, set()
    for line in file[line_num + 1:]:
        for v in get_vars(to_correct_case(line)):
            if v in seen:
                continue
            seen.add(v)
            res += 1
            if res == 10:
                return var
            if v == var:
                return str(res)
    return var


def default_for_functions(parts):
    return parts


def abbreviate_line(line):
    line_ln, end, new_line = len(line), -1, []
    for i, char in enumerate(line):
        if i < end:
            continue
        if len(char) > 1 and i + 2 < line_ln and line[i + 1] == ' ' and len(line[i + 2]) > 1:
            end = i + 2
            res = ABBREVIATIONS[char] + ABBREVIATION
            while end < line_ln and line[end - 1] == ' ' and len(line[end]) > 1:
                res += ABBREVIATIONS[line[end]]
                end += 2
            new_line.append(res)
            end -= 1
        else:
            new_line.append(char)
    return ''.join(new_line)


def shorten_num(num, changed):
    res, cnt = '', 0
    if len(num) > 0 and num[0] == '0':
        return num, False
    for dig in num:
        if dig == '_':
            continue
        elif dig == '0':
            if cnt == 26:
                res += chr(90)
                cnt = 0
            cnt += 1
        else:
            if cnt > 0:
                res += chr(64 + cnt)
                cnt = 0
            res += dig
    if cnt > 0:
        res += chr(64 + cnt)
    if len(res) >= len(num):
        res = num
    # base = BASE_62 + to_base_62(num)
    # if len(base) < len(res):
    #     res = base
    return res, changed or res != num


def to_base_62(num):
    num = int(num)
    base = len(ALPHABET)
    first = str(num % 10)
    res = ''
    num = num // 10
    while num:
        res += ALPHABET[num % base]
        num //= base
    res = first + res[::-1]
    return res or "0"


def replace_numbers(line):
    parts = re.findall(r'((?<!\w)(?:(?<!`)\d[\d_]*)|.)', line)
    changed = False
    for v, val in enumerate(parts):
        if len(val) > 1:
            for i in 'beox':
                if i in val:
                    continue
            parts[v], changed = shorten_num(val, changed)
    # return '1'
    return ''.join(parts) if changed else line


def split_raise_except(line):
    parts = ['', '', '']
    parts[0] = 'raise' if line.startswith('raise') else 'except'
    line = line[len(parts[0]):]
    amount_open = 0
    line = line.strip()
    while len(line) > 0 and (re.match(r'[^\s]', line[0]) or amount_open > 0):
        amount_open += count_brackets_single(line[0])
        if line[0] in ['f', 'a'] and amount_open == 0 and len(parts[1]) > 0 and parts[1][-1] == ')':
            break
        parts[1] += line[0]  # can optimize to use indexes instead of constantly popping
        line = line[1:]
    line = line.strip()

    to_strip = 0 if len(line) == 0 else {'f': 4, 'a': 2}[line[0]]
    parts[2] = line[to_strip:]
    return [x.strip() for x in parts]


# TODO except(Exception1, Exception2)
def throw_except(line):
    # (raise|except)(?: (\w+(?:\([^\s]+\))?)(?: from (\w+(?:\([^\s]+\))))?)?
    # parts = re.match(r'(raise|except)(?: (\w[^\s]*(?:\([^\s]+\))?)(?: ?from (\w[^\s]*(?:\([^\s]+\))?))?)?').groups()
    parts = split_raise_except(line)
    is_raise = parts[0] == 'raise'
    exception = parts[1]
    if exception is None:
        return line
    start = 't' if is_raise else 'e'
    line = '!' + start + compress_exception(exception)
    if parts[2] != '':
        line += (FROM if is_raise else AS) + compress_exception(parts[2])
    return line


def compress_exception(exception):  # maybe can pass Exception an object?
    if exception in EXCEPTIONS:
        return EXCEPTIONS[exception]
    # if exception.startswith('Exception('):
    #     exception = exception[len('Exception('):-1]
    # else:
    exception = exception
    return exception


def replace_common_functions(line):
    # for i in BUILT_IN_FUNCTIONS:
    #     if functions.count(i) > 1:
    #         print(i)
    for i, func in enumerate(BUILT_IN_FUNCTIONS):
        if func in line:
            line = re.sub(r'\b' + func + r'\(', f'{ to_base_62(i) }(', line)
    return line


def remove_spaces_line(line):
    line = line.strip()
    i = 0
    while i < len(line):
        char = line[i]
        if char in [' ', '   ', '\n']:
            if not (re.match(r'\w', line[i - 1]) and
                    re.match(r'\w', line[i + 1])):
                line = line[:i] + line[i + 1:]
                i -= 1
        i += 1
    return line


def remove_spaces_all(file, index):
    for i, line in enumerate(file):
        if i < index:
            continue
        file[i] = remove_spaces_line(line)
    return file


def put_brackets(input_file, comments):
    indentation = comment_count = 0
    ends_with_colon = re.compile(r':\s*(' + COMMENT + ')?$')
    # is_function_call = re.compile(r'\w+\((.*)\)')
    for i, line in enumerate(input_file):
        tabs = count_tabs(line)
        line = line.strip()
        judge_by = get_judge_by(line, comments, comment_count)
        comment_count += 1 if COMMENT in line else 0

        amount_to_indent = indentation - tabs
        indentation = tabs

        # 3 issue is multilined function calls since eg:
        # func(1, # one
        #      02, # two
        #      )
        # function_args = is_function_call.fullmatch(line.strip())
        # if indentation == 0 and function_args is not None:
        #     function_args = function_args.group(1)
        #     if count_brackets(function_args) == 0:
        #         print(function_args)

        if starts_with_indent_keyword(judge_by) in ['elif', 'else', 'except', 'finally']:
            amount_to_indent -= 1
            if amount_to_indent == -1:
                line = DONT_UNINDENT + line
        if ends_with_colon.search(judge_by):
            line = ends_with_colon.sub(r'\1', line)
            indentation += 1
        input_file[i] = CLOSE_INDENT * amount_to_indent + line


def multiline_comments(file):
    file_ln = len(file)
    end = -1
    for i, line in enumerate(file):
        if i <= end:
            continue
        if line[0] == '#' and i + 1 < file_ln and file[i + 1][0] == '#':
            end = i
            file[i] = MULTILINE_COMMENT + line[1:]
            while end + 1 < file_ln and file[end + 1][0] == '#':
                end += 1
                file[end] = file[end][1:]
                if len(file[end]) > 0 and file[end][0] == MULTILINE_COMMENT:
                    file[end] = ' ' + file[end]
            file[end] = MULTILINE_COMMENT + file[end]


def remove_comments(file, strings):
    comments, to_pop = [], []
    amount_of_open = 0
    removing = False
    for l, line in enumerate(file):
        valid_line = get_before_comment(line)
        amount_of_open += count_brackets(valid_line)

        if removing:
            if STR in line:
                line = restore_specific_str(file, line, l, strings)
            if amount_of_open == 0:
                line_actual_lines = line.split('\n')
                for i, ln in enumerate(line_actual_lines):
                    if comments[-1] != '':
                        comments[-1] += '\n'
                        if i == len(line_actual_lines) - 1:
                            comments[-1] += MULTILINE_COMMENT
                    comments[-1] += ln.strip()
                to_pop.append(l)
                comments[-1] = DONT_KNOW + comments[-1]
                # file[l+1] = '$' + file[l+1]
                removing = False
            else:
                comments[-1] += '\n' + line.strip()
                to_pop.append(l)

        else:
            if amount_of_open != 0:
                removing = True
                if STR in line:
                    restored_line = restore_specific_str(file, line, l, strings)
                    comments.append(restored_line.strip())
                else:
                    comments.append(line.strip())
                file[l] = count_tabs(file[l]) * '\t' + COMMENT
                # remove previous lines until one with open bracket
                open_, i = amount_of_open, l
                while True:
                    valid_line = get_before_comment(line)  # todo dont count brackets in string
                    open_ -= count_brackets(valid_line)
                    if i != l:
                        if i < 0:
                            raise Exception("ohoh")
                        to_pop.append(i)
                        if STR in line:
                            line = restore_specific_str(file, line, i, strings)
                        comments[-1] = line.strip() + '\n' + comments[-1]
                    line, i = file[i - 1], i - 1
                    if open_ == 0:
                        break
            elif '#' in line:
                pos = line.index('#')
                comments.append('#' + line[pos + 1:].strip())
                file[l] = line[:pos] + COMMENT
    for i in to_pop[::-1]:
        file.pop(i)
    return comments


def join_multilines(file):  # maybe?
    to_join = []
    amount_of_open = 0
    for i, line in enumerate(file):
        valid_line = get_before_comment(line)
        amount_of_open += count_brackets(valid_line)
        if amount_of_open != 0:
            if '#' not in line:
                to_join.append(i)
        elif line.strip()[-1] == '\\':
            file[i] = line.strip()[:-1]

            to_join.append(i)
    for i in to_join[::-1]:
        file[i] += ' ' + file.pop(i + 1).strip()


def number_functions(file):
    functions, doubles = set(), set()
    for line in file:
        line = line.strip()
        if line.startswith('def '):
            name = line[len('def '):line.index('(')]
            if name in doubles:
                continue
            if name in functions:
                doubles.add(name)
                functions.remove(name)
            else:
                functions.add(name)
    res, i = {}, 0
    for f in functions:
        if len(str(i)) < len(f):
            res[f] = str(i)
            i += 1
    return res

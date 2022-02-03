import re
from sys import argv
from black import format_str as black_format_str, FileMode
from DeCompressFunctions import *
from ReplaceSymbols import *


def decompress_for(file, line, line_num, comments):
    parts = line[2:].split(IN)
    names = ', '.join(get_names(file, parts[0].split(','), line_num, comments))
    iters = ', '.join(default_for_functions(parts[1]))
    return 'for ' + names + ' in ' + iters


def get_names(file, vars, line_num, comments):
    res, mx = [], -1
    for var in vars:
        if is_num(var):
            for v in var:
                mx = max(mx, int(v))

    if mx == -1:
        return vars

    next_vars = get_vars_till(file, line_num, mx, comments)
    for var in vars:
        if is_num(var):
            for v in var:
                res.append(next_vars[int(v)])
        else:
            res.append(var)
    return res


def get_vars_till(file, line_num, till, comments):
    seen = []
    for line_num in range(line_num + 1, len(file)):
        line = decompress_all(file, -1, comments, specific_line=line_num)
        for v in get_vars(line):
            if v in seen:
                continue
            seen.append(v)
            if len(seen) > till:
                return seen
    return seen


def decompress_all(file, indx, comments, specific_line=None):
    indentation = comment_count = 0
    num_re = re.compile(r'[^\w]\d')
    following_checks_re = re.compile(r'\w@\w+')
    in_brackets = 0
    in_str = False
    for i, line in enumerate(file):
        if i <= indx:
            continue
        if specific_line is not None:
            i, line = specific_line, file[specific_line]
        if line[0] == DONT_UNINDENT:
            indentation += 1
            line = line[1:]
        comment_count += 1 if COMMENT in line else 0
        if '!' in line:
            if COMPREHENSION_RANGE in line:
                line = re.sub(COMPREHENSION_RANGE + r'(\w+)', r'\1 for \1 in', line)
            if FOR_IN_RANGE_NAME in line:
                line = re.sub(FOR_IN_RANGE_NAME + r'(\w+)\(', r'for \1 in range(', line)
            if FOR_IN_RANGE in line:
                line = line.replace(FOR_IN_RANGE, 'for _ in range(')
            if OR in line:
                line = line.replace(OR, ' or ')
            if AND in line:
                line = line.replace(AND, ' and ')
            if NOT in line:
                line = line.replace(NOT, ' not ')
            if IS in line:
                line = line.replace(IS, ' is ')
            if INIT in line:
                line = line.replace(INIT, ' __init__ ')
            if TRUE in line:
                line = line.replace(TRUE, ' True ')
            if FALSE in line:
                line = line.replace(FALSE, ' False ')
            if BASE_62 in line:
                line = re.sub(BASE_62 + r'[\da-zA-Z]+', to_normal_base, line)
        if EVEN in line:
            line = line.replace(EVEN, '%2==0')
        if ODD in line:
            line = line.replace(ODD, '%2!=0')
        if CAMEL_CASE in line:
            line = to_snake_case(line)
        if re.search(r'\b\d\w*\(', line):
            line = re.sub(r'\b\d\w*(?=\()', put_back_built_in_functions, line)
        if num_re.search(line):
            line = restore_nums(line)
        if GROUPED_NUMS in line:
            line = ungroup_nums(line)

        while line[0] == CLOSE_INDENT:
            line = line[1:]
            indentation -= 1

        is_comment = line.endswith(COMMENT)
        if is_comment:
            line = line[:-COMMENT_LEN]
            if line == '':

                judge_by = get_judge_by(COMMENT, comments, comment_count - 1, with_remove=False)

                line = '    ' * indentation + COMMENT
                if len(judge_by) != 0 and judge_by[0] != '#':
                    indent_word = starts_with_indent_keyword(judge_by)
                    if indent_word is not None and in_brackets == 0:
                        if indent_word in ['elif', 'else', 'except', 'finally']:
                            line = line[4:]
                        else:
                            indentation += 1
                start = in_str if in_str else ''
                before_comment = [start + get_before_comment(judge_by) + start]
                remove_strings(before_comment, True)
                in_brackets += count_brackets(before_comment[0])
                before_comment = [start + get_before_comment(judge_by)]     # todo sketchhyy
                in_str = remove_strings(before_comment, True)   # todo sketchhyy

                if specific_line is not None:
                    return line
                file[i] = line
                continue

        line = close_brackets(line)
        in_brackets += count_brackets(line)
        if line.startswith(CLASS):
            line = line.replace(CLASS, 'class ', 1)
        elif line[0] == END_IMPORTS:
            file[i] = line[1:]
            indx, indentation = replace_imports(file, i, indentation)
            if is_comment:
                file[i] += '\t' + COMMENT
            continue
        elif line[0] == DEF:
            line = 'def ' + line[1:]
        elif line[0] == IF:
            line = 'if ' + line[1:]
        elif line.startswith(RAISE) or line.startswith(EXCEPT):
            line = decompress_exception_raise(line)
        elif line.startswith(FOR) and IN in line:
            line = decompress_for(file, line, i, comments)
        elif line.startswith(WHILE):
            if line == WHILE:
                line = 'while True'
            else:
                line = 'while ' + line[2:]
        elif line.startswith(RETURN):
            line = 'return ' + line[2:]
        elif line.startswith('else') and line != 'else':
            line = 'elif' + line[len('else'):]

        if line.startswith('def '):
            line = put_back_self(line, True)
            line = line.replace('=,', '=None,').replace('=)', '=None)')
            line = init_param(file, line, i)
            if line.startswith('def ('):
                if line == 'def ()':
                    line = 'def __init__(self)'
                else:
                    line = line.replace('def (', 'def __init__(', 1)
                # if line == 'def __init__()':
                #     line = 'def __init__(self)'
        else:
            line = put_back_self(line, False)

        if following_checks_re.search(line):
            line = replace_following(line, following_checks_re)
        line, indentation = indent(indentation, line, comments, comment_count, in_brackets)

        if line.endswith('++') or line.startswith('--'):
            line = line[:-1] + '=1'

        if is_comment:
            line += '\t' + COMMENT

        if specific_line is not None:
            return line

        file[i] = line


def decompress(compressed_file, output_file):
    if not compressed_file or compressed_file == ['']:
        return ''
    # if output_file is None:
    #     output_file = open(r'D:\Aharon\git\ajs-code\python\PythonCompressionAlgorithm\first.py', 'w', encoding='utf8')
    strings = remove_strings(compressed_file)
    comments = remove_comments(compressed_file, strings)
    indx, _ = replace_imports(compressed_file)
    decompress_all(compressed_file, indx, comments)
    put_back(compressed_file, comments, COMMENT, False)
    put_back(compressed_file, strings, STR, False)

    res = '\n'.join(compressed_file)
    # todo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # todo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    res = black_format_str(res, mode=FileMode())
    # res = black_format_str(res, mode=FileMode(target_versions={TargetVersion.PY310}))
    # todo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # todo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # todo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if output_file:
        output_file.write(res)
        output_file.close()
    return res


def main():
    # try:
    with open(argv[1]) as input_file:
        output_file = open(argv[2], 'w')
        decompress(input_file.read().split('\n'), output_file)
    # except Exception:
    #     print(Exception)
    #     print('input should be in the following format:')
    #     print('file_to_open.txt file_to_output.txt is_lossy')


if __name__ == '__main__':
    main()

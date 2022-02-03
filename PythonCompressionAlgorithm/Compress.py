import copy
import time
import threading
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from sys import argv
from pathlib import Path

from Decompress import put_back
from Decompress import decompress
from CompressFunctions import *

from black import format_str as black_format_str, FileMode
from black.parsing import InvalidInput


# $ - multiline comment
# @ - is not = isnt //// while
# 2648160


def compress_all(file, indx, is_lossy, functions):
    check_st = '(?:is|not|in|or|and|None|True|False)'
    following_tokens = re.compile(r'((?:(?<!\w)' + check_st + r'(?!\w))|.)')
    following_checks = re.compile(f'{check_st} {check_st}')
    for i, line in enumerate(file):
        if i <= indx:
            continue
        line = line.strip()  # is this neccesery? if not also erase the file[i] =line
        is_comment = line.endswith(COMMENT)
        if is_comment:
            all_close = CLOSE_INDENT * (len(line) - COMMENT_LEN)
            if line == all_close + COMMENT:
                file[i] = line
                continue
            line = line[:-1 * COMMENT_LEN]
        amount_of_close, line = count_close_brackets(line)
        line = shorten_for_common_usses(line)
        if len(line) > 0:
            match line[0]:
                case 'f' | 'i':
                    if re.search(r'^(import|from)\b', line):
                        indx = replace_imports(file, i)
                        amount_of_close, line = count_close_brackets(file[i])
                        file[i] = CLOSE_INDENT * amount_of_close + END_IMPORTS + line
                        continue
                    elif line[0] == 'f':
                        if re.search(r'^for\b', line):
                            line = compress_for(file, line, i)
                    else:   # 2 i
                        if re.search(r'^if\b', line):
                            line = compress_if(line)
                case 'e' | 'r':
                    if re.search(r'^(except|raise)\b.', line):
                        line = throw_except(line)
                    elif line[0] == 'e':
                        if line == 'except':
                            line = EXCEPT
                        elif re.search(r'^elif\b', line):
                            line = 'else' + line[len('elif'):]
                    else:   # 2 r
                        if line == 'raise':
                            line = RAISE
                        elif re.search(r'^return\b', line):
                            to_return = line[len('return'):].strip()
                            if to_return == 'None':
                                to_return = ''
                            line = RETURN + to_return
                case 'w':
                    if re.search(r'^while\b', line):
                        line = compress_while(line)
                case 'c':
                    if re.search(r'^class\b', line):
                        line = line.replace('class ', CLASS, 1)

            # elif line.startswith()
            if line.startswith('def '):
                line = init(file, line, i)
                line = line.replace('=None,', '=,').replace('=None)', '=)')
                if line.startswith('def __init__('):
                    line = re.sub(r'def __init__\(\s*self', 'def (', line, 1)
                line = DEF + line[len('def '):]
            elif re.match(r'\w+\(', line):
                line = replace_functions(line, functions)

            # if '%' in line:
            #     line = re.sub(r'%2==0\b', EVEN, line)
            #     line = re.sub(r'%2!=0\b', ODD, line)

            if '{' in line and line.count(':') > 1 and contains_dict(line):
                # print(line)
                pass
            #     line = replace_dict(line)

            if following_checks.search(line):
                line = abbreviate_line(following_tokens.findall(line))

            if digits_and_commas_re.search(line):
                line = numbers_with_commas(line)
            line = replace_numbers(line)
            line = replace_common_words(line)

            if line.endswith('+=1'):
                line = line[:-len('+=1')] + '++'
            elif line.endswith('-=1'):
                line = line[:-len('-=1')] + '--'

            while line[-1] in CLOSE_BRACKETS:
                line = line[:-1]
        line = CLOSE_INDENT * amount_of_close + line
        if is_comment:
            line += COMMENT
        line = replace_common_functions(line)
        file[i] = line


def compress(file, output_file, is_lossy):
    if not file or file == ['']:
        return file, False
    # file_str = '\n'.join(file)
    # looking_re = re.compile(r'if[^\n]+:\n\s+return\b')
    # if looking_re.search(file_str):
    #     global looking_count
    #     looking_count += len(looking_re.findall(file_str))
    #     print(looking_count)
        
    strings = remove_strings(file)
    # remove_same_strings__FAIL__(strings)

    remove_empty_lines(file)
    join_multilines(file)
    comments = remove_comments(file, strings)
    # outer_comments = join_multilines(file, [])
    functions = number_functions(file)
    functions = {}  # 4 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    to_camel_case(file)
    indx = replace_imports(file)
    put_brackets(file, comments)
    remove_spaces_all(file, indx)
    compress_all(file, indx, is_lossy, functions)
    put_back(file, comments, COMMENT, is_lossy)
    put_back(file, strings, STR, False)
    multiline_comments(file)
    file_str = '\n'.join(file)
    output_file.write(file_str)
    output_file.close()
    return file_str.split('\n'), True  # splitting after joining for multiline strings


def remove_same_strings__FAIL__(strings):
    strings_to_pos = {}
    for i, s in enumerate(strings):
        if s not in strings_to_pos:
            strings_to_pos[s] = i
    string_id, string_ids = 0, {}
    for i, s in enumerate(strings):
        pos = strings_to_pos[s]
        if pos != i:
            id_ = string_id
            if s in string_ids:
                id_ = string_ids[s]
            else:
                string_ids[s] = id_
                strings[pos] += str(id_)
                string_id += 1
            strings[i] = "@" + str(id_)


def both(func, *a):
    for val in a:
        func(val)


def main():
    start_time = time.time()
    args = argv
    if len(args) == 1:
        args = ['', r'D:\Aharon\git\ajs-code\python\PythonCompressionAlgorithm\InputFile.py',
                r'D:\Aharon\git\ajs-code\python\PythonCompressionAlgorithm\new.txt']
    global file_count, abs_path
    if len(args) == 5:
        p = Path('D:\\cygwin64\\' + args[1])
        with ProcessPoolExecutor() as pool:
            for path in p.rglob('*'):
                abs_path = str(path.resolve())
                if abs_path.endswith('.py'):
                    file_count += 1
                    # process_file(abs_path, args, path)
                    pool.submit(process_file, abs_path, args, path)
    else:
        output_file = open(args[2], 'w', encoding='utf8')
        with open(args[1], encoding='utf8') as input_file:
            is_lossy = (args[2].lower() == 'true') if len(args) > 3 else False
            ipt = input_file.read()
            try:
                ipt = black_format_str(ipt, mode=FileMode()).split('\n')
            except InvalidInput:
                print('!!!!!!!!!!!!!!!!!!!!!!! INVALID INPUT !!!!!!!!!!!!!!!!!!!!!!!')
                output_file.write(ipt)
                output_file.close()
            else:

                ipt_cpy = [line for line in ipt]
                compressed, successful = compress(ipt, output_file, is_lossy)
                if successful:
                    output_file = open(r'D:\Aharon\git\ajs-code\python\PythonCompressionAlgorithm\first.py', 'w',
                                       encoding='utf8')

                    decompressed = decompress(compressed, output_file).split('\n')
                    both(remove_empty_lines, ipt_cpy, decompressed)
                    check_if_same(decompressed, ipt_cpy)

    print(f"took {time.time() - start_time} time")


def process_file(path_abs, args, path):
    with open(path, encoding='utf8') as input_file:
        ipt = input_file.read()
    try:
        ipt = black_format_str(ipt, mode=FileMode()).split('\n')
    except InvalidInput:
        print('!!!!!!!!!!!!!!!!!!!!!!! INVALID INPUT !!!!!!!!!!!!!!!!!!!!!!! in:')
        print(path_abs)
    else:
        ipt_cpy = [line for line in ipt]
        output_file = open(path_abs, 'w', encoding='utf8')
        is_lossy = args[2].lower() == 'true'
        is_fast = args[3].lower() == 'true'
        compressed, successful = compress(ipt, output_file, is_lossy)
        if successful:
            if not is_fast:
                decompressed = decompress(compressed, None).split('\n')
                both(remove_empty_lines, ipt_cpy, decompressed)
                is_same = check_if_same(decompressed, ipt_cpy)
                if not is_same:
                    print(path_abs)
        else:
            if ipt and ipt != ['']:
                print(path_abs)


abs_path = ""
file_count = 0
same_st = 0
looking_count = 0
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(file_count)
        print(f"ERROR IN: {abs_path}")
        raise e

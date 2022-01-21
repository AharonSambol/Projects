import time
import threading
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from sys import argv
from pathlib import Path

from Decompress import put_back
from Decompress import decompress
from CompressFunctions import *

from black import black_format_str, FileMode
from black.parsing import InvalidInput

# $ - multiline comment
# @ - is not = isnt //// while
# 2584


def compress_all(file, indx, is_lossy, functions):
    check_st = '(?:is|not|in|or|and|None|True|False)'
    following_tokens = re.compile(r'((?:(?<!\w)' + check_st + r'(?!\w))|.)')
    following_checks = re.compile(f'{check_st} {check_st}')
    for i, line in enumerate(file):
        if i < indx:
            continue
        line = line.strip()  # is this neccesery? if not also erase the file[i] =line
        is_comment = line.endswith('!comment!')
        if is_comment:
            all_close = '}' * (len(line) - len('!comment!'))
            if line == all_close + '!comment!':
                file[i] = line
                continue
            line = line[:-1 * len('!comment!')]

        amount_of_close = 0
        while len(line) > 0 and line[0] == '}':
            line = line[1:]
            amount_of_close += 1
        if len(line) > 0:
            if 'for _ in range(' in line:
                line = re.sub(r'\bfor _ in range\(', '^^', line)
            if line == 'except':
                line = 'e!'
            elif line == 'raise':
                line = 't!'
            elif re.search(r'^(except|raise)\b', line):
                line = throw_except(line)
            elif re.search(r'^if\b', line):
                line = compress_if(line)
            elif re.search(r'^for\b', line):
                line = compress_for(file, line, i)
            elif re.search(r'^while\b', line):
                line = compress_while(line)
            elif re.search(r'^return\b', line):
                line = '<-' + line[len('return'):].strip()
            elif re.search(r'^elif\b', line):
                line = 'else' + line[len('elif'):]
            # elif line.startswith()

            if line.startswith('def '):
                line = init(file, line, i)
                line = line.replace('=None,', '=,').replace('=None)', '=)')
            elif re.match(r'\w+\(', line):
                line = replace_functions(line, functions)

            if '{' in line and line.count(':') > 1 and contains_dict(line):
                # print(line)
                pass
            #     line = replace_dict(line)

            if following_checks.search(line):
                line = abreviate_line(following_tokens.findall(line))

            if digits_and_commas_re.search(line):
                line = numbers_with_commas(line)
            line = replace_numbers(line)
            line = replace_common_words(line)

            if line.startswith('def '):  # TODO WHY TF IS THIS BETTER HERE???
                line = '~' + line[len('def '):]

            while line[-1] in CLOSE_BRACKETS:
                line = line[:-1]
        line = '}' * amount_of_close + line
        if is_comment:
            line += '!comment!'
        file[i] = line


def compress(file, output_file, is_lossy):
    if not file or file == ['']:
        return file, False
    strings = remove_strings(file)
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
    put_back(file, comments, '!comment!', is_lossy)
    put_back(file, strings, '!str!', False)
    multiline_comments(file)
    output_file.write('\n'.join(file))
    output_file.close()
    return '\n'.join(file).split('\n'), True  # for multiline strings


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
        all_executors = []
        with ProcessPoolExecutor() as pool:

            for path in p.rglob('*'):
                abs_path = str(path.resolve())
                if abs_path.endswith('.py'):
                    file_count += 1
                    all_executors.append(pool.submit(process_file, abs_path, args, path))
    else:
        output_file = open(args[2], 'w', encoding='utf8')
        with open(args[1], encoding='utf8') as input_file:
            is_lossy = (args[2] in ['True', 'true']) if len(args) > 3 else False
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
                    output_file = open(r'D:\Aharon\git\ajs-code\python\PythonCompressionAlgorithm\first.py', 'w', encoding='utf8')

                    decompressed = decompress(compressed, output_file).split('\n')
                    both(remove_empty_lines, ipt_cpy, decompressed)
                    check_if_same(decompressed, ipt_cpy)

    print(f"took {time.time() - start_time} time")


def process_file(abs_path, args, path):
    with open(path, encoding='utf8') as input_file:
        ipt = input_file.read()
    try:
        ipt = black_format_str(ipt, mode=FileMode()).split('\n')
    except InvalidInput:
        print('!!!!!!!!!!!!!!!!!!!!!!! INVALID INPUT !!!!!!!!!!!!!!!!!!!!!!!')
    else:
        ipt_cpy = [line for line in ipt]
        output_file = open(abs_path, 'w', encoding='utf8')
        is_lossy = (args[2] in ['True', 'true']) if len(args) > 3 else False
        compressed, successful = compress(ipt, output_file, is_lossy)
        if successful:
            decompressed = decompress(compressed, None).split('\n')
            both(remove_empty_lines, ipt_cpy, decompressed)
            is_same = check_if_same(decompressed, ipt_cpy)
            if not is_same:
                print(abs_path)
        else:
            if ipt and ipt != ['']:
                print(abs_path)


abs_path = ""
file_count = 0
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(file_count)
        print(f"ERROR IN: { abs_path }")
        raise e

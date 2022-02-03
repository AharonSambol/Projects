import re
from black import format_str as black_format_str, FileMode
from Decompress import get_before_comment


def count_tabs(line):
    arr = re.findall(r'(    |\t|.)', line)
    i = 0
    while i < len(arr) and arr[i] in ['\t', '    ']:
        i += 1
    return i


def remove_empty_lines(file):
    lines_to_pop = []
    for i, line in enumerate(file):
        if line.strip() == '':
            lines_to_pop.append(i)
    for i in lines_to_pop[::-1]:
        file.pop(i)


def check_if_same_new_version(file1, file2):
    i = j = 0
    in_digit = False
    while True:
        col1 = col2 = 0
        while True:
            if in_digit:
                if file1[i][col1] == '_':
                    col1 += 1
                if file2[i][col2] == '_':
                    col2 += 1
            if col1 >= len(file1[i]):
                i += 1
                col1 = 0
            if col2 >= len(file2[j]):
                j += 1
                col2 = 0
            char1, char2 = file1[i][col1], file2[j][col2]
            if not are_the_same(char1, char2):
                print(file1[i], '~~~~~~~~~~~~~~~~~~~~', file2[j])
                return False
            col1 += 1
            col2 += 1
            if re.match(r'.\b\d', file1[i][col1-1:col1+1]):
                in_digit = True


def are_the_same(char1, char2):
    if char1 == char2:
        return True
    if char1 in ['"', "'"] and char2 in ["'", '"']:
        return True
    return False


def check_if_same(decompressed, ipt_cpy):
    remove_empty_comments(ipt_cpy)
    same = True
    for file in [ipt_cpy, decompressed]:
        i = 0
        in_str = False
        while i < len(file):
            line = file[i]
            line, in_str = get_before_comment(line, in_str, 2)
            line = line.replace(',)', ')')
            if line.strip() == "":
                file.pop(i)
            else:
                if i + 1 < len(file) and file[i+1].strip()[0] in ")]}":
                    while line[-1] in [',', ' ', '\t']:
                        line = line[:-1]
                file[i] = line
                i += 1
        # print('\n'.join(file))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    ipt_cpy = '\n'.join(ipt_cpy)
    decompressed = '\n'.join(decompressed)
    ipt_cpy = re.sub(r'(?<=\d)_(?=\d)', '', ipt_cpy)
    decompressed = re.sub(r'(?<=\d)_(?=\d)', '', decompressed)

    ipt_cpy = black_format_str(ipt_cpy, mode=FileMode()).split('\n')
    decompressed = black_format_str(decompressed, mode=FileMode()).split('\n')

    remove_empty_lines(ipt_cpy)
    remove_empty_lines(decompressed)

    for line1, line2 in zip(ipt_cpy, decompressed):
        if line1.strip() != line2.strip() and not is_okay_mistake(line1, line2):
            print(f'original:   {line1}')
            print(f'mistake:    {line2}')
            print('----------------------')
            return False
    if not same:
        print('POSSIBLE COMMENT ERROR')
    return same


def disintegrate_comments(file):
    i = 0
    while i < len(file):
        if len(file[i]) > 0 and file[i].strip()[0] == '#':
            file.pop(i)
        else:
            if '#' in file[i]:
                file[i] = get_before_comment(file[i])
            i += 1
    remove_empty_lines(file)
    return black_format_str('\n'.join(file), mode=FileMode()).split('\n')


def remove_empty_comments(file):
    i = 0
    while i < len(file):
        if file[i].strip() == '#':
            file.pop(i)
        else:
            i += 1


def is_okay_mistake(line1, line2):
    if count_tabs(line1) != count_tabs(line2):
        return False
    st1 = line1.strip()
    st2 = line2.strip()
    init_assignment = re.compile(r'self\.(\w+) = \1')
    if len(st1) > 0 and len(st2) > 0:
        if st1[0] in ['"', "'"] and st2[0] in ['"', "'"]:
            if st1.strip(st1[0]) == st2.strip(st2[0]):
                return True
        elif init_assignment.match(st1) and init_assignment.match(st2):
            return True
    if st1[0] == st2[0] == '#':
        if st1[1:].strip() == st2[1:].strip():
            return True
    return_none = ['return None', 'return']
    if st1 in return_none and st2 in return_none:
        return True
    return False

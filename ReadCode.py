import re

from Math.operations import evaluate_line, start, split_code


def compile_functions(code):
    code = list(code)
    i = 0
    while i < len(code):
        if (i + 4 < len(code) and code[i: i + 4] == list('def ')) and\
                (i - 1 < 0 or code[i - 1] in [' ', '\n', '\t']):
            for _ in range(4):  # 3 pop 'def '
                code.pop(i)
            func_name = get_func_name(code, "", i)
            args = get_func_args(code, i)
            func = get_func_body(code, "", i)
            global functions
            functions[func_name] = (args, func[:-1].strip())
        i += 1
    return code


def get_func_body(code, func, i):
    open_brackets = 1
    while open_brackets > 0:
        if code[i] == "(":
            open_brackets += 1
        elif code[i] == ")":
            open_brackets -= 1
        func += code[i]
        code.pop(i)
    return func


def get_func_args(code, i):
    args = [""]
    while code[i] != ":":
        if i + 1 == len(code):
            raise Exception("function must include ':' for parameters")
        if code[i] == " ":
            args.append("")
        else:
            args[-1] += code[i]
        code.pop(i)
    code.pop(i)
    return args


def get_func_name(code, func_name, i):
    while code[i] != "(":
        if i + 1 == len(code):
            raise Exception("Unclosed (")
        if code[i] != " ":
            func_name += code[i]
        code.pop(i)
    code.pop(i)
    return func_name


def eval_code_block(code_block, variables):
    returned = [False]
    for line in split_code(code_block):
        variables, returning = evaluate_line(line.strip(), variables)
        if returning[0] != [False]:
            returned = returning

    print("~~~~~~~~~~~~vars~~~~~~~~~~~~~")
    for key in variables.keys():
        print(key, ":", variables[key])
    print("~~~~~~~~~~~funcs~~~~~~~~~~~~~")
    for key in functions.keys():
        print(key, ":", functions[key])
    print("\n\n")
    return variables, returned


if __name__ == '__main__':
    functions = dict()
    start(eval_code_block, functions)
    with open('codeIDE.txt') as reader:
        code_txt = "".join(compile_functions(reader.read())).strip()
        code_txt = re.sub('((?<![a-zA-Z]) | (?![a-zA-Z]))', '', code_txt)
        eval_code_block(code_txt, dict())

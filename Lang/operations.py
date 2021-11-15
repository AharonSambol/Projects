from Lang.VarTypes.VarType import *

IF_WHILE_FOR = re.compile("\\(.*\\)(?:\\?:?|->)\\(.*?\\)")
IF_WHILE_FOR_WithGroups = re.compile("\\((.+)\\)(\\?:?|->)(\\(.*?\\))")
STR_CONST = re.compile("\".*?\"")
MATRIX_CONST = re.compile("\\[\\|.*?\\|]")
LIST_CONST = re.compile("\\[.*?]")
ITER_CONST = re.compile("{.*?}")
BOOL_CONST = re.compile("true|false")
FUNCTION = re.compile("[a-zA-Z]\\w*!?\\??(?:\\[\\d+])?\\(")
VARIABLES = re.compile("[a-zA-Z]\\w*!?\\??(?:\\[\\??\\d+])?")
BRACKETS = re.compile("[()\\[\\]{}:]")
OPERATORS = re.compile("\\*|%\\??|//|/|\\+|==|!=|<=|>=|@>|<@|<|>|@=@|,|-|\\.|&|\\|\\||=|!")
NUMBER = re.compile("-?\\d+(?:\\.\\d+)?")
EACH_ARG = re.compile("<arg>.+</arg>")
REGEX = re.compile(f"(;|{ EACH_ARG.pattern }|{ IF_WHILE_FOR.pattern }|{ STR_CONST.pattern }|"
                   f"{ MATRIX_CONST.pattern }|{ LIST_CONST.pattern }|{ BOOL_CONST.pattern }|{ ITER_CONST.pattern }"
                   f"{ FUNCTION.pattern }|{ VARIABLES.pattern }|{ BRACKETS.pattern }|"
                   f"{ OPERATORS.pattern }|{ NUMBER.pattern }|.)")
VAR_ATTRIBUTE = re.compile("([\\w\\d?]+)\\[(.+)]")
FIRST_LAST_BRACKETS = re.compile("(^\\(|^<|>$|\\)$)")
INSTANTIATING_LINE = re.compile("((?:\\w|\\d|\\[.+])+)\\s*([+-])?=\\s*(.*)")
FUNC_LINE = re.compile("(\\w+)\\((.*)\\)")

eval_code_block_func = lambda x, y: 0
functions = {None: [[None]]}


def start(eval_code_block, funcs):
    global eval_code_block_func, functions
    functions = funcs
    eval_code_block_func = eval_code_block


def split_code(code):
    new_code = ""
    in_brackets = 0
    for c in code:
        if c == ';' and in_brackets == 0:
            new_code += '\n'
        else:
            if c == '(':
                in_brackets += 1
            elif c == ')':
                in_brackets -= 1
            new_code += c
    return new_code.split("\n")


def evaluate_line(line_st, variables):
    to_return = [False]
    if line_st.startswith("//") or re.fullmatch("\\s*", line_st):    # 3 comment \ empty line
        return variables, to_return
    line_st = line_st.replace("++", "+=1").replace("--", "-=1")
    if match := re.match(INSTANTIATING_LINE, line_st):
        instantiating(match, variables)
    elif match := re.match(FUNC_LINE, line_st):
        to_return[0] = calculate_full_expression(match.group(0), variables)
    elif line_st.startswith("~"):
        to_return[0] = evaluate_line(line_st[1:].strip(), variables)[1]
    else:
        to_return[0] = calculate_full_expression(line_st, variables)
    return variables, to_return


def calculate_full_expression(equation, variables):
    equation = wrap_each_funcs(equation)
    equation = split_to_parts(equation)
    equation = restitch(equation)
    equation = remove_vars(equation, variables)
    equation = calc_funcs(equation, variables)
    equation = turn_everything_to_type(equation, variables)
    return calc_math(equation, variables)


def wrap_each_funcs(equation):
    first_args = False
    if 'each' not in equation:
        if 'all?' not in equation:
            if 'any?' not in equation:
                return equation
            else:
                pos = equation.index('any?') + len('any?(')
        else:
            pos = equation.index('all?') + len('all?(')
    else:
        pos = equation.index('each') + len('each(')
    in_br = 0
    i = pos
    while i < len(equation):
        val = equation[i]
        if val == ')' and in_br == 0:
            if first_args:
                equation = equation[:i] + '</arg>' + equation[i:]
            break
        if val in ['(', '[', '{']:
            in_br += 1
        elif val in [')', ']', '}']:
            in_br -= 1
        if val == ',' and in_br == 0:
            if first_args:
                equation = equation[:i] + '</arg>' + equation[i:]
                i += len('</arg>')
            first_args = True
            equation = equation[:i+1] + '<arg>' + equation[i+1:]
            i += len('<arg>')
        i += 1
    return equation


def parse_if_while_for_func(match, variables, is_while=False):
    flag = re.sub(FIRST_LAST_BRACKETS, "", match[0])
    if type(b := calculate_full_expression(flag, variables)) is Bool:
        parts = re.sub(FIRST_LAST_BRACKETS, "", match[2]).split(":")
        if is_while:
            return b.value, split_code(":".join(parts).strip())
        if b.value:
            return parts[0].strip()
        else:
            return ":".join(parts[1:]).strip()


def instantiating(match, variables):
    val = calculate_full_expression(match.group(3), variables)
    var = match.group(1)
    posses = False
    if '[' in var:
        var, *posses = re.split("[\\[\\]]", var)
        posses = [calculate_full_expression(x, variables) for x in posses if x]

    if match.group(2) == "+" and var in variables:
        if posses:
            variables[var].change_by(val, posses)
        else:
            variables[var] += val
    elif match.group(2) == "-":
        if var in variables:
            if posses:
                variables[var].change_by(Int(0) - val, posses)
            else:
                variables[var] -= val
        else:
            if type(val) in [Int, Float]:
                if posses:
                    variables[var].change_at(Int(0) - val, posses)
                else:
                    variables[var] = Int(0) - val
            else:
                _ = val - 0     # 3 raises exception
    else:
        if posses:
            variables[var].change_at(val, posses)
        else:
            variables[var] = copy.copy(val)


def split_to_parts(equation):
    return re.findall(REGEX, equation)


def restitch(equation):
    i = 0
    while i < len(equation):
        val = equation[i]
        if val.endswith('$'):
            equation[i] += equation[i+1]
            equation.pop(i+1)
            continue
        if val.startswith("."):
            if val == '.':
                equation[i] += equation[i + 1]
                equation.pop(i + 1)
            equation[i - 1] += equation[i]
            equation.pop(i)
            i -= 1
            continue
        if i > 0 and re.fullmatch(NUMBER, val):
            if equation[i-1] == '-' and (i == 1 or not equation[i-2].isnumeric()):
                equation[i-1] += equation[i]
                equation.pop(i)
                i -= 1
                continue
        if "(" in val or "[" in val or "{" in val:
            if i > 0 and ((val.startswith("(") and
                           (equation[i - 1][-1].isalpha() or equation[i - 1][-1] in ['!', '?', '$']))
                          or (re.match("[]a-zA-Z).]", equation[i-1][-1]))):
                equation[i - 1] += equation[i]
                equation.pop(i)
                i -= 1
            amount_of_open = 0
            for b in [('(', ')'), ('[', ']'), ('{', '}')]:
                amount_of_open += val.count(b[0]) - val.count(b[1])
            while amount_of_open > 0:
                amount_of_open -= equation[i + 1].count(")") + equation[i + 1].count("]") + equation[i + 1].count("}")
                amount_of_open += equation[i + 1].count("(") + equation[i + 1].count("[") + equation[i + 1].count("{")
                equation[i] += equation[i + 1]
                equation.pop(i + 1)
        i += 1
    return equation


def split_attributes(var):
    attributes = [""]
    in_par = False
    amount_of_par = 0
    for i, c in enumerate(var):
        if c == "(":
            amount_of_par += 1
            in_par = True
        elif c == ")":
            amount_of_par -= 1
            in_par = amount_of_par > 0
        elif c == "." and not in_par and not var[i+1].isdigit() and var[i-1] != '>':
            attributes.append("")
            continue
        attributes[-1] += c
    return attributes


def remove_vars(equation, variables):
    for i, par in enumerate(equation):
        if re.match(IF_WHILE_FOR_WithGroups, par):
            if_while_for(equation, i, par, variables)
            continue
        var_components = split_attributes(par)
        name = var_components[0]

        if "[" in name and re.match("^\\w+\\??\\[", name):
            var, *posses = re.split("[\\[\\]]", name)
            j = 0
            posses = [calculate_full_expression(x, variables) for x in posses if x]
            while j < len(posses):
                if type(posses[j]) is str and posses[j].startswith('?'):
                    posses[j] = '?' + str(calculate_full_expression(posses[j][1:], variables))
                else:
                    posses[j] = calculate_full_expression(str(posses[j]), variables)
                j += 1

            match = re.match(VAR_ATTRIBUTE, name)
            name = match.group(1)
            if name.endswith('?'):
                name = name[:-1]
                if name not in variables:
                    equation[i] = Bool(False)
                    continue
            var = variables[name]
            for pos in posses:
                var = var.get_at([pos])
            if len(var_components) > 1:
                equation[i] = evaluate_var_params(var, var_components[1:], variables)
            else:
                equation[i] = var
            continue
        if name.endswith('?') and name != '%?':
            name = name[:-1]
            if name not in variables:
                equation[i] = Bool(False)
                continue
        if name in variables:
            if len(var_components) > 1:
                equation[i] = evaluate_var_params(variables[name], var_components[1:], variables)
            else:
                equation[i] = variables[name]
        else:
            name = turn_everything_to_type([name], variables)[0]
            if type(name) is not str:
                if len(var_components) > 1:
                    equation[i] = evaluate_var_params(name, var_components[1:], variables)
                else:
                    equation[i] = name

    return equation


def split_if_while_for(equation):
    arr = [""]
    open_bra = 0
    for i in range(len(equation)):
        c = equation[i]
        if c == '(':
            if arr != [''] and arr[-1].count('(') - arr[-1].count(')') == 0:
                arr.append('')
            open_bra += 1
        elif c == ')':
            open_bra -= 1
        elif c == '?' and open_bra == 0 and arr[-1][-1] != '?':
            arr.append('')
        elif i < len(equation) - 1 and equation[i:i+2] == '->' and open_bra == 0:
            arr.append('')
        arr[-1] += c
    return [x.strip() for x in arr]


def split_for_args(args):
    lst = [""]
    in_br = 0
    for c in args:
        if c == ',' and in_br == 0:
            lst.append("")
            continue
        elif c in ['(', '[']:
            in_br += 1
        elif c in [']', ')']:
            in_br -= 1
        lst[-1] += c
    return lst


def if_while_for(equation, i, par, variables):
    match = split_if_while_for(equation[i])
    if match[1] == '?':  # 3 if
        equ = parse_if_while_for_func(match, variables)
        for line in split_code(equ):
            a = evaluate_line(line, variables)[1][0]
            if a is not None:
                equation[i] = a
        if equation[i] is None:
            equation[i] = Bool(False)

    elif match[1] == '?:':  # 3 while
        condition = lambda: parse_if_while_for_func(match, variables, is_while=True)
        cond, code = condition()
        while cond:
            for line in code:
                evaluate_line(line.strip(), variables)
            cond, code = condition()
        if not match[2].startswith('<'):
            equation.pop(i)
    elif match[1] == '->':    # 3 for
        name = 'None'
        loop_range = split_for_args(match[0][1:-1])
        if len(loop_range) == 2:

            name = loop_range[0]
            loop_range = loop_range[1].split(':')   # 2 maybe change this to an unused character like $
        else:
            loop_range = match[0][1:-1].split(':')

        for i in range(len(loop_range)):
            if loop_range[i] in variables:
                loop_range[i] = variables[loop_range[i]]
            else:
                loop_range[i] = calculate_full_expression(loop_range[i], variables)

        if len(loop_range) == 1:
            if type(loop_range[0]) is Iterable:
                enumerate_iter(loop_range, name, par, variables)
                return
            if loop_range[0].value > 0:
                loop_range = [Int(0), loop_range[0]]
            else:
                loop_range = [loop_range[0], Int(0)]

        if len(loop_range) > 2:
            raise Exception("didn't program this yet")
        if name != 'None':
            variables[name] = loop_range[0]
            end = loop_range[1].value
            while variables[name].value < end:
                evaluate_line(par.split('->', 1)[1][1:-1], variables)
                variables[name] = variables[name] + Int(1)
            del variables[name]
        else:
            for _ in range(loop_range[0].value, loop_range[1].value):
                evaluate_line(par.split('->', 1)[1][1:-1], variables)


def enumerate_iter(loop_range, name, par, variables):
    pos = 'None'
    var = name.split(':')
    if len(var) > 1:
        var, pos = var
    else:
        var = var[0]
    itr = loop_range[0]
    if var != 'None':
        i = 0
        while itr.has():
            if pos != 'None':
                variables[pos] = Int(i)
            variables[var] = itr.pop()
            evaluate_line(par.split('->', 1)[1][1:-1], variables)
            i += 1
        del variables[var]
        if pos in variables:
            del variables[pos]
    else:
        while itr.has():
            itr.pop()
            evaluate_line(par.split('->', 1)[1][1:-1], variables)


def calc_funcs(equation, variables):
    if len(equation) == 0:
        return equation
    for i in range(len(equation)):
        word = equation[i]
        if type(word) is not str or not re.match("[a-zA-Z].+\\(", word) or word in ['true', 'false']:
            continue
        var_components = split_attributes(word)
        func, args = extract_func_args(var_components.pop(0))
        if args == ['']:
            _, returned = eval_code_block_func(functions[func][1], dict())
        else:

            args = [calculate_full_expression(str(x), variables) for x in args]
            if func == 'print':
                print_func(args)
                returned = [Bool(False)]
            elif func == 'each':
                lst = []
                for val in args[0].value:
                    if len(args) > 1:
                        if check_condition(condition=args[1], val=val, variables=variables).value:
                            if len(args) == 3:
                                lst.append(do_action(action=args[2], val=val, variables=variables))
                            else:
                                lst.append(val)
                    else:
                        lst.append(val)
                returned = [Iterable(lst)]
            elif func == 'all?':
                returned = [Bool(True)]
                for val in args[0].value:
                    if not check_condition(condition=args[1], val=val, variables=variables).value:
                        returned = [Bool(False)]
                        break
            elif func == 'any?':
                returned = [Bool(False)]
                for val in args[0].value:
                    if check_condition(condition=args[1], val=val, variables=variables).value:
                        returned = [Bool(True)]
                        break
            else:
                new_variables = dict()
                params = functions[func][0]

                for arg, param in zip(args, params):
                    new_variables[param] = arg
                # 1 if one of args is iterable the while iter.has(): eval_code(iter.pop())
                _, returned = eval_code_block_func(functions[func][1], new_variables)
            if len(var_components) != 0:
                returned[0] = evaluate_var_params(returned[0], var_components, variables)
        equation[i] = returned[0]
    return equation


def check_condition(condition=None, val=None, variables=None):
    new_vars = copy.deepcopy(variables)
    new_vars['#'] = val
    condition = condition.replace('<arg>', '').replace('</arg>', '').strip()
    return calculate_full_expression(condition, new_vars)


def do_action(action=None, val=None, variables=None):
    new_vars = copy.deepcopy(variables)
    new_vars['#'] = val
    action = action.replace('<arg>', '').replace('</arg>', '').strip()
    return calculate_full_expression(action, new_vars)


def extract_func_args(func):
    func_name = func.split("(")[0]
    func = func[len(func_name) + 1: -1]
    args = [""]
    in_par = False
    amount_of_par = 0
    for c in func:
        if c in ["(", "[", "{"]:
            amount_of_par += 1
            in_par = True
        elif c in [")", "]", "}"]:
            amount_of_par -= 1
            in_par = amount_of_par > 0
        elif c == "," and not in_par:
            args[-1] = args[-1].strip()
            args.append("")
            continue
        args[-1] += c
    return func_name, args


def call_function(val, function, variables, args=None):
    if function.endswith('!'):
        function = function[:-1]
    else:
        val = copy.copy(val)
    if args is None:
        return val.functions[function]()
    if function == "sort":
        args.append(calc_funcs)
        return val.functions[function](packed=args, variables=variables)
    return val.functions[function](packed=args)


def evaluate_var_params(var, orig_params, variables):
    try:
        posses = []
        params = orig_params
        for param in params:
            if param.endswith("]"):
                param, *posses = re.split('[\\[\\]]', param)
                posses = [calculate_full_expression(x, variables) for x in posses if x]

            if "(" in param:
                function, args = extract_func_args(param)
                if function.startswith('$'):
                    if not function.endswith('!'):
                        var = copy.copy(var)
                    function = function[1:]

                    for i, val in enumerate(var.value):
                        try:
                            if args[0] == '':
                                var.value[i] = call_function(val, function, variables)
                            else:
                                args = [calculate_full_expression(str(x), variables) for x in args]
                                var.value[i] = call_function(val, function, variables, args=args)
                        except AttributeError:
                            var.value[i] = Bool(False)
                    return var
                elif args[0] == '':
                    var = call_function(var, function, variables)
                else:
                    args = [calculate_full_expression(str(x), variables) for x in args]
                    var = call_function(var, function, variables, args=args)
            else:
                var = var.attributes[param]()
            for pos in posses:
                var = var.get_at(packed=[pos])
    except AttributeError:
        return Bool(False)
    return var


def turn_everything_to_type(equation, variables):
    for i, val in enumerate(equation):
        if type(val) is str:
            if re.match(STR_CONST, val):
                equation[i] = String(val[1:-1], variables)
            elif val in ["true", "false"]:
                equation[i] = Bool(val)
            elif re.fullmatch(NUMBER, val):
                equation[i] = Float(float(val)) if "." in val else Int(int(val))
            elif re.match(MATRIX_CONST, val):
                lst = []
                val = matrix_split(val)
                if type(val[0]) is Int:
                    equation[i] = Matrix(val[0])
                    continue
                for row in val:
                    lst.append([])
                    for c in row:
                        if c == '':
                            continue
                        calculated = calculate_full_expression(c.strip(), variables)
                        lst[-1].append(calculated)
                if not all([len(arr) == len(lst) for arr in lst]):
                    equation[i] = Bool(False)
                    continue
                equation[i] = Matrix(lst)
            elif re.match(LIST_CONST, val):
                if val.startswith('[*'):
                    equation[i] = List(int(val[2:-1]))
                    continue
                lst = []
                val = list_split(val)
                for c in val:
                    if c == '':
                        continue
                    calculated = calculate_full_expression(c.strip(), variables)
                    lst.append(calculated)
                equation[i] = List(lst)
            elif re.match(ITER_CONST, val):
                lst = []
                val = list_split(val)
                for c in val:
                    if c == '':
                        continue
                    calculated = calculate_full_expression(c.strip(), variables)
                    lst.append(calculated)
                equation[i] = Iterable(lst)
    return equation


def calc_math(equation, variables):
    if len(equation) == 0:
        return equation
    remove_calculated = lambda arr, index: [arr.pop(index) for _ in range(2)]
    if len(equation) == 1 and re.fullmatch('\\(.+\\)', str(equation[0])):
        equation = [calculate_full_expression(str(equation[0])[1:-1], variables)]
    while "(" in equation:
        pos, length = find_parentheses(equation)
        sub_eq = []
        for _ in range(length - 1):
            sub_eq.append(equation.pop(pos))
        sub_eq.pop(0)
        equation[pos] = calc_math(sub_eq, variables)
    while "@" in equation:
        pos = equation.index("@")
        equation[pos + 1] = Int(equation[pos + 1].value)
        equation.pop(pos)
    while "^" in equation:
        pos = equation.index("^")
        equation[pos - 1] = equation[pos - 1] ** equation[pos + 1]
        remove_calculated(equation, pos)
    while "*" in equation:
        pos = equation.index("*")
        equation[pos - 1] = equation[pos - 1] * equation[pos + 1]
        remove_calculated(equation, pos)
    while "/" in equation:
        pos = equation.index("/")
        equation[pos - 1] = equation[pos - 1] / equation[pos + 1]
        remove_calculated(equation, pos)
    while "//" in equation:
        pos = equation.index("//")
        equation[pos - 1] = equation[pos - 1] // equation[pos + 1]
        remove_calculated(equation, pos)
    while "%" in equation:
        pos = equation.index("%")
        equation[pos - 1] = equation[pos - 1] % equation[pos + 1]
        remove_calculated(equation, pos)
    while "%?" in equation:
        pos = equation.index("%?")
        equation[pos - 1] = Bool((equation[pos - 1] % equation[pos + 1]).value == 0)
        remove_calculated(equation, pos)
    while "-" in equation:
        pos = equation.index("-")
        if pos == 0:
            equation[0] = Int(0) - equation[1]
            equation.pop(1)
        else:
            equation[pos - 1] = equation[pos - 1] - equation[pos + 1]
            remove_calculated(equation, pos)
    while "+" in equation:
        pos = equation.index("+")
        equation[pos - 1] = equation[pos - 1] + equation[pos + 1]
        remove_calculated(equation, pos)

    i = 1
    while i < len(equation):
        if type(equation[i]) != str and type(equation[i-1]) != str:
            equation[i-1] += equation[i]
            equation.pop(i)
            continue
        i += 1

    while "!" in equation:
        pos = equation.index("!")
        equation[pos + 1] = Bool(not equation[pos + 1].value)
        equation.pop(pos)
    while "==" in equation:
        pos = equation.index("==")
        equation[pos - 1] = Bool(equation[pos - 1] == equation[pos + 1])
        remove_calculated(equation, pos)
    while "!=" in equation:
        pos = equation.index("!=")
        equation[pos - 1] = Bool(equation[pos - 1] != equation[pos + 1])
        remove_calculated(equation, pos)
    while ">" in equation:
        pos = equation.index(">")
        equation[pos - 1] = Bool(equation[pos - 1] > equation[pos + 1])
        remove_calculated(equation, pos)
    while "<" in equation:
        pos = equation.index("<")
        equation[pos - 1] = Bool(equation[pos - 1] < equation[pos + 1])
        remove_calculated(equation, pos)
    while "<=" in equation:
        pos = equation.index("<=")
        equation[pos - 1] = Bool(equation[pos - 1] <= equation[pos + 1])
        remove_calculated(equation, pos)
    while ">=" in equation:
        pos = equation.index(">=")
        equation[pos - 1] = Bool(equation[pos - 1] >= equation[pos + 1])
        remove_calculated(equation, pos)
    while "@=@" in equation:
        pos = equation.index("@=@")
        equation[pos - 1] = Bool(sorted(equation[pos - 1].value) == sorted(equation[pos + 1].value))
        remove_calculated(equation, pos)
    while "@>" in equation:
        pos = equation.index("@>")  # 3 all values in obj1 are in obj2
        equation[pos - 1] = Bool(all(x in equation[pos + 1].value for x in equation[pos - 1].value))
        remove_calculated(equation, pos)
    while "<@" in equation:
        pos = equation.index("<@")  # 3 all values in obj2 are in obj1
        equation[pos - 1] = Bool(all(x in equation[pos - 1].value for x in equation[pos + 1].value))
        remove_calculated(equation, pos)
    while "&" in equation:
        pos = equation.index("&")
        equation[pos - 1] = Bool(
            equation[pos - 1].attributes["is?"]().value and
            equation[pos + 1].attributes["is?"]().value)
        remove_calculated(equation, pos)
    while "||" in equation:
        pos = equation.index("||")
        equation[pos - 1] = Bool(
            equation[pos - 1].attributes["is?"]().value or
            equation[pos + 1].attributes["is?"]().value)
        remove_calculated(equation, pos)

    return equation[0]


def find_parentheses(equation):
    pos, length, amount_of_open = -1, 0, 0
    for i, char in enumerate(equation):
        if char == "(":
            pos = i if pos == -1 else pos
            amount_of_open += 1
        elif char == ")":
            amount_of_open -= 1
            if amount_of_open == 0:
                return pos, length + 1
        if amount_of_open > 0:
            length += 1


def print_func(packed=None):
    params = [str(x)[1:-1] if type(x) is String else str(x) for x in packed]
    params = " ".join(params)
    print(params)

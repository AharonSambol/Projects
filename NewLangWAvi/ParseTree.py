from HelperFunctions import *
import re


def eval_tree(node, in_list_comprehension=False):
    global extension_class
    # print(node.value)
    if node.children:
        res = close_function(node)
        if res:
            return res
        res = insert_function(node)
        if res:
            return res
    match node.value.type:
        case ParsedTokens.PROGRAM:
            res = ""
            for n in node.children:
                if n.value.type == ParsedTokens.NEW_LINE:
                    continue
                n.value = f"{eval_tree(n)}"
                if n.value and not n.value.endswith('}') and not n.value.endswith(';'):
                    n.value += ';'
                res += n.value + '\n'
            return f"{{\n{res}\n}}"
        case ParsedTokens.MODULO | ParsedTokens.MULTIPLICATION | ParsedTokens.DIVISION | ParsedTokens.ADDITION \
                | ParsedTokens.SUBTRACTION | ParsedTokens.BOOL_OR | ParsedTokens.BOOL_AND | ParsedTokens.BOOL_EQ \
                | ParsedTokens.BOOL_NEQ | ParsedTokens.BOOL_SEQ | ParsedTokens.BOOL_LEQ | ParsedTokens.BOOL_S \
                | ParsedTokens.BOOL_L:
            return f"{eval_tree(node.children[0])} {token_to_symbol[node.value.type]} {eval_tree(node.children[1])}"
        case ParsedTokens.XOR:
            first = eval_tree(node.children[0])
            second = eval_tree(node.children[1])
            return f"(({first} && !{second}) || (!{first} && {second}))"
        case ParsedTokens.NAND:
            return f"!({eval_tree(node.children[0])} && {eval_tree(node.children[1])})"
        case ParsedTokens.BOOL_IN:
            return f"{eval_tree(node.children[1])}.Contains({eval_tree(node.children[0])})"
        case ParsedTokens.BOOL_NOT_IN:
            return f"!{eval_tree(node.children[1])}.Contains({eval_tree(node.children[0])})"
        case ParsedTokens.CEILING_DIVISION:
            return f"((int)Math.Ceiling((double){eval_tree(node.children[0])}/(double){eval_tree(node.children[1])}))"
        case ParsedTokens.FLOOR_DIVISION:
            return f"((int)Math.Floor((double){eval_tree(node.children[0])}/(double){eval_tree(node.children[1])}))"
        case ParsedTokens.PARENTHESES | ParsedTokens.INDEX | ParsedTokens.LIST:
            typ = res = ""
            is_len = False
            for i, child in enumerate(node.children):
                if node.value.type == ParsedTokens.LIST and child.value.type == ParsedTokens.COLON:
                    if typ:
                        if res[:-len(', ')] == 'len':
                            is_len = True
                            res = ""
                            continue
                        else:
                            raise Exception("Type already declared in this list")
                    typ = res[:-len(', ')]
                    typ = cast_type(typ)
                    res = ""
                    continue
                res += str(eval_tree(child))
                if i + 1 != len(node.children):
                    res += ', '
            if node.value.type == ParsedTokens.PARENTHESES:
                if node.value.name:
                    return f"( {res} )"
                else:
                    return f"{res} )"
            if node.value.type == ParsedTokens.INDEX:
                return f"[ {res} ]"
            if typ == "":
                raise Exception("Lists must be given a type eg: [int: 1, 2, 3]")
            if is_len:
                return f"new {list_class}<{typ}>(new {typ}[{res}].ToList())"
            if res == "":
                return f"new {list_class}<{typ}>(new List<{typ}>())"
            return f"new {list_class}<{typ}>(new List<{typ}>(){{ {res} }})"
        case ParsedTokens.POW:
            return f"Math.Pow({eval_tree(node.children[0])}, {eval_tree(node.children[1])})"
        case ParsedTokens.BOOL_NOT:
            return f"!{eval_tree(node.children[0])}"
        case ParsedTokens.INT | ParsedTokens.FLOAT | ParsedTokens.NULL | ParsedTokens.BOOL:
            return node.value.name
        case ParsedTokens.STR:
            return f'new {str_class}("{node.value.name}")'
        case ParsedTokens.ASSIGNMENT:
            child = node.children[0]
            if child.value.type == ParsedTokens.CONST:
                child = child.children[0]
            valid = child.value.type == ParsedTokens.UNKNOWN
            while valid:
                if child.value.type != ParsedTokens.UNKNOWN:
                    valid = False
                if len(child.children) == 0:
                    break
                child = child.children[0]
            if valid:
                program = move_up_tree_while(node, lambda n: n.value.type != ParsedTokens.PROGRAM)
                var_name = eval_tree(node.children[0])
                var_name = cast_type(var_name)
                if ' ' in var_name:
                    program.declared_vars.append(var_name.split(' ')[-1])
                    return f"{var_name} {node.value.name} {eval_tree(node.children[1])}"
                if var_name in get_all_var_names(program):
                    return f"{var_name} {node.value.name} {eval_tree(node.children[1])}"
                program.declared_vars.append(var_name)
                return f"var {var_name} {node.value.name} {eval_tree(node.children[1])}"
            # print(f"{node.parent.value=}, {node.value}")
            return f"{eval_tree(node.children[0])} {node.value.name} {eval_tree(node.children[1])}"
        case ParsedTokens.CONDITION_STATEMENT:
            if len(node.children) == 1:
                cond, block = Tree(Token(ParsedTokens.BOOL, True), node), node.children[0]
            else:
                cond, block = node.children[0], node.children[1]
            name = node.value.name
            if name == 'unless':
                return f"if (!({eval_tree(cond)})) {eval_tree(block)}"
            if name == 'until':
                return f"while (!({eval_tree(cond)})) {eval_tree(block)}"
            if name == 'loop':
                if len(node.children) == 1:
                    return f"while (true) {eval_tree(block)}"
                global loop_var_name
                loop_var_name += 1
                # 2 while re.search(r'\b_____' + str(loop_var_name) + r'\b', code_str):
                # 2    loop_var_name += 1
                return f"foreach(var _____{loop_var_name} in Enumerable.Range(0, {eval_tree(cond)})) {eval_tree(block)}"
            if name == 'elif':
                name = 'else if'
            if name == 'else':
                return f"else {eval_tree(block)}"
            if name == 'case':
                block.children.append(Tree(Token(ParsedTokens.CONTROL_MODIFIER, 'break'), block))
                return f"{name} {eval_tree(cond)}:\n{eval_tree(block)[1:-1].strip()}"
            return f"{name} ({eval_tree(cond)}) {eval_tree(block)}"
        case ParsedTokens.FOR_LOOP:
            assign_vars = node.children.pop(0).value.name
            all_declared_vars = get_all_var_names(node)
            if assign_vars not in all_declared_vars and not in_list_comprehension:
                assign_vars = 'var ' + assign_vars
            is_multiple = False
            while node.children[0].value.type not in [ParsedTokens.IN, ParsedTokens.INDEX_KEYWORD]:
                name = node.children.pop(0).value.name
                if name not in all_declared_vars and not in_list_comprehension:
                    name = 'var ' + name
                assign_vars += ", " + name
                is_multiple = True
            if is_multiple:
                assign_vars = f"({assign_vars})"

            in_or_index = node.children.pop(0).value.name
            iter_var = eval_tree(node.children.pop(0))
            # 4 from *var* x in arr
            if in_list_comprehension:  # 3 list comprehension
                if in_or_index == "in":
                    return f"from {assign_vars} in {iter_var}"
                else:
                    raise Exception("Don't support that type of list comprehension yet (use 'in' instead of 'index')")
                    # return f"for(int {assign_vars}=0; {assign_vars} < {iter_var}.Length; {assign_vars}++) " \
                    #        f"{eval_tree(node.children[-1])}"

            if in_or_index == "in":
                return f"foreach({assign_vars} in {iter_var}) {eval_tree(node.children[0])}"
            else:
                return f"for({assign_vars}=0; {assign_vars} < {iter_var}.len; {assign_vars}++) " \
                       f"{eval_tree(node.children[-1])}"
        case ParsedTokens.CONTROL_MODIFIER:
            match node.value.name:
                case 'return':
                    if node.children:
                        return f"return {eval_tree(node.children[0])}"
                    return 'return'
                case 'break' | 'continue' | 'rewind' | 'restart':
                    if node.children:
                        return f'goto {eval_tree(node.children[0])}__{node.value.name}__'
                    if node.value.name in ['rewind', 'restart']:
                        raise Exception(f'{node.value.name} only works with a reference to a specific loop, '
                                        f'using a Tag (# loop1) for now')
                    return node.value.name
        case ParsedTokens.FUNCTION:
            if len(node.children) == 3:
                return_types = node.children.pop(0).value.name
                return_types = cast_type(return_types)
                if ',' in return_types:
                    return_types = f"({return_types})"
            else:
                return_types = "void"
            # 3 flatten input variables:
            is_extension = False
            prev_type = ""

            ipt_param = node.children[0]
            for n in ipt_param.children:
                parts = []
                if n.value.type == ParsedTokens.ASSIGNMENT:
                    parts.append(n.children.pop(0))
                    while parts[-1].children:
                        parts.append(parts[-1].children[0])
                parts.append(n)
                while parts[-1].children:
                    parts.append(parts[-1].children[0])
                # print([x.value.name for x in parts])
                start = default = ""
                if parts[0].value.name in ['extend', 'out', 'ref']:
                    start = {'extend': 'this', 'out': 'out', 'ref': 'ref'}[parts[0].value.name] + ' '
                    parts.pop(0)
                if len(parts) > 1 and parts[-2].value.name == '=':
                    parts.pop(-2)
                    default = f"={parts.pop().value.name}"
                if len(parts) == 2:
                    prev_type = parts[0].value.name if parts[0].value.name != 'str' else str_class
                    name = parts[1].value.name
                else:
                    name = parts[0].value.name
                n.value = Token(ParsedTokens.UNKNOWN, f"{ start }{prev_type} {name}{default}")
                n.children = []
            passed_vars = eval_tree(node.children[0])
            all_names = list(re.findall(r'\w+(?=\s*[,=)])', passed_vars))
            node.children[1].declared_vars.extend(all_names)
            if is_extension:
                extension_methods.append(f"public {return_types} {node.value.name} {passed_vars} "
                                         f"{eval_tree(node.children[1])}")
                return ""
            return f"public {return_types} {node.value.name} {passed_vars} " \
                   f"{eval_tree(node.children[1])}"
        case ParsedTokens.DOT:
            return f"{eval_tree(node.children[0])}.{eval_tree(node.children[1])}"
        case ParsedTokens.GO_TO:
            loop = node.children[0]
            loop_body = loop.children[-1]
            loop_body.children.insert(0,
                                      Tree(Token(ParsedTokens.UNKNOWN, f"{node.value.name}__rewind__:{{}}"),
                                           loop_body))
            return f"{node.value.name}__restart__:{{}} \n" \
                   f"{eval_tree(loop)[:-1]} " \
                   f"{node.value.name}__continue__:{{}} \n" \
                   f" }} \n" \
                   f"{node.value.name}__break__:{{}}"  # .replace('{', '{ goto__rewind__', 1)
        case ParsedTokens.REMOVE_NULL_DEFAULT:
            if len(node.children) == 1:
                return f"{extension_class}.Cast({eval_tree(node.children[0])})"
            return f"{extension_class}.Cast({eval_tree(node.children[0])}, {eval_tree(node.children[1])})"
        case ParsedTokens.LIST_COMPREHENSION:
            if node.children[1].value.type != ParsedTokens.COLON:
                raise Exception("Type required in list comprehension eg: [str: x for x...")
            typ = node.children.pop(0).value.name
            typ = cast_type(typ)
            node.children.pop(0)
            if len(node.children) == 2:
                return f"new {list_class}<{typ}>(({eval_tree(node.children[1], in_list_comprehension=True)} " \
                       f"select {eval_tree(node.children[0], in_list_comprehension=True)}).ToList())"
            else:  # 3 (len == 3)
                condition = node.children[2]
                term, condition = condition.value.name, condition.children[0]
                if term == 'if':
                    condition = f"{eval_tree(condition)}"
                elif term == 'unless':
                    condition = f"!({eval_tree(condition)})"
                return f"new {list_class}<{typ}>(({eval_tree(node.children[1], in_list_comprehension=True)} " \
                       f"where {condition} " \
                       f"select {eval_tree(node.children[0], in_list_comprehension=True)}).ToList())"
        case ParsedTokens.DOT_DOT:
            is_lst = node.children.pop(0).value.name
            if is_lst:
                return f"new {list_class}<int>(" \
                       f"Enumerable.Range({eval_tree(node.children[0])}, {eval_tree(node.children[1])})" \
                       f".ToList())"
            else:
                if len(node.children) == 1:
                    return f"[{ eval_tree(node.children[0]) }..]"
                return f"[{ eval_tree(node.children[0]) }..{eval_tree(node.children[1])}]"

        case ParsedTokens.UNKNOWN | ParsedTokens.CONST:
            res = node.value.name
            for c in node.children:
                res += " " + eval_tree(c)
            if (node.parent.value.type == ParsedTokens.PROGRAM and
                    len(node.children) == 1 and node.children[0].value.type == ParsedTokens.UNKNOWN and
                    not node.children[0].children):
                program = move_up_tree_while(node, lambda n: n.value.type != ParsedTokens.PROGRAM)
                program.declared_vars.append(res.split(' ')[-1])
                return res + '= default'
            return res
        case ParsedTokens.NEW_LINE:
            return ''
        case ParsedTokens.NEGATIVE:
            return f"-{eval_tree(node.children[0])}"
        # case ParsedTokens.PIPE:
        #     pass
        case ParsedTokens.DICT:
            key_type = node.children.pop(0).value.name
            key_type = cast_type(key_type)
            value_type = node.children.pop(0).value.name
            value_type = cast_type(value_type)
            node.children.pop(0)  # 3 colon
            init_values = ""
            while node.children:
                key = eval_tree(node.children.pop(0))
                node.children.pop(0)  # 3 colon
                val = eval_tree(node.children.pop(0))
                init_values += f"{{ {key}, {val} }},"
            return f"new Dictionary<{key_type}, {value_type}>(){{ {init_values} }} "
        case ParsedTokens.SET:
            typ = node.children.pop(0).value.name
            typ = cast_type(typ)
            node.children.pop(0)  # 3 colon
            init_values = ""
            while node.children:
                val = eval_tree(node.children.pop(0))
                init_values += f"{val}, "
            return f"new HashSet<{typ}>(){{ {init_values} }} "
        case ParsedTokens.TRY_CATCH_FINALLY:
            match node.value.name:
                case 'try':
                    this_node = node.parent.children.index(node)
                    if len(node.parent.children) > this_node + 1:
                        next_node = node.parent.children[this_node + 1].value
                        if next_node.type == ParsedTokens.TRY_CATCH_FINALLY and next_node.name == 'fix':
                            return f'try {eval_tree(node.children[0])}'
                    return f'try { eval_tree(node.children[0]) } catch (System.Exception){{}}'
                case 'fix':
                    if len(node.children) == 1:
                        return f'catch(System.Exception) {eval_tree(node.children[0])}'
                    return f'catch {eval_tree(node.children[0])} {eval_tree(node.children[1])}'
                case 'finally':
                    return f'finally { eval_tree(node.children[0]) }'
        case ParsedTokens.THROW:
            return f'throw { eval_tree(node.children[0]) }'
        case ParsedTokens.CLASS_TYPE:
            typ = {
                'Obj': 'class',  # 2 unless its a record
                'StaticObj': 'static class',  # 2 unless its a record
                'Struct': 'struct',
                'Type': 'enum',
                'Instructions': 'interface',
                'Record': 'record'
            }[node.value.name]
            if typ == 'record':
                param = ""
                for child in node.children[0].children[0].children:
                    param += eval_tree(child) + ", "
                param = f"({param.removesuffix(', ')})"
                return f'record {node.children[0].value.name} ' \
                       f'{parse_param(param)}'
            inheritance = ''
            for child in node.children[1].children:
                if child.value.name == '~':
                    continue
                if child.value.type not in [ParsedTokens.CLASS_PARTS, ParsedTokens.NEW_LINE]:
                    if typ in ['enum', 'interface']:
                        continue
                    raise Exception("Class must only contain these parts: "
                                    "['extends', 'implements', 'vars', 'staticVars', 'funcs', 'staticFuncs'] "
                                    f"not {child.value.name}")
                if child.value.name in ['extends', 'implements']:
                    for cls in child.children[0].children:
                        if re.fullmatch(r'\w+', cls.value.name):
                            inheritance += cls.value.name + ', '
            if inheritance:
                inheritance = ' : ' + inheritance.removesuffix(', ')
            name = eval_tree(node.children[0])

            body = node.children[1]
            change_all_children(body, {'obj': ('this', False), 'cls': (name, False)})

            body = eval_tree(body)
            if typ == 'interface':
                body = re.sub(r'(?:^|\n)(\s*\w+\s*\()', r'\nvoid \1', body)
                body = re.sub(r'(\w\s*)(\(.+\))(?=;\n)', parse_param_re, body)
            if typ == 'enum':
                body = body.replace(';', ',')
            return f"public {typ} {name}{inheritance} {body}"
        case ParsedTokens.PLUS_PLUS:
            return f"{eval_tree(node.children[0])}{node.value.name}"
        case ParsedTokens.CLASS_PARTS:
            res = ""
            match node.value.name:
                case '~':
                    class_name = node.parent.parent.children[0].value.name
                    name_no_generic = re.sub(r'<\w+>$', '', class_name)
                    node.value = Token(ParsedTokens.FUNCTION, f'public { name_no_generic }')
                    # 3 deal with the "@"s
                    to_add = []
                    for i, child in enumerate(node.children[0].children):
                        parent = node.children[0]
                        while child.children:
                            if child.value.name == '@':
                                parent.children[i] = child.children[0]
                                name = parent.children[i].value.name
                                to_add.append(
                                    Tree(
                                        Token(
                                            ParsedTokens.UNKNOWN,
                                            f'this.{name} = {name}'
                                        ), node.children[1]
                                    )
                                )
                            parent = child
                            child = child.children[0]
                            i = 0
                    node_body = node.children[1]
                    node_body.children = to_add + node_body.children
                    return eval_tree(node).removeprefix('public void ')
                case 'extends' | 'implements':
                    return ''
                case 'vars' | 'staticVars':
                    prefix = {'vars': 'public', 'staticVars': 'public static'}[node.value.name]
                    for child in node.children[0].children:
                        var = eval_tree(child)
                        if var:
                            res += f'{prefix} {var};\n'
                    return res.removesuffix(';\n')
                case 'funcs' | 'staticFuncs':
                    for child in node.children[0].children:
                        var = eval_tree(child)
                        if var:
                            if node.value.name == 'staticFuncs':
                                res += f'public static {var.removeprefix("public ")}\n'
                            else:
                                res += f'{var}\n'
                    return res.removesuffix('\n')
                case _:  # todo constructor
                    raise Exception(f"Invalid part of class {node.value.name}")
        case _:
            raise Exception(f"Unsupported parsed type {node.value}")


def change_all_children(node, replace_dict):
    for child in node.children:
        if child.value.type == ParsedTokens.UNKNOWN and child.value.name in replace_dict:
            to, rem = replace_dict[child.value.name]
            if rem:
                if child.children[0].value.type == ParsedTokens.PARENTHESES:
                    child.children[0].value = Token(ParsedTokens.PARENTHESES, '')
            child.value = Token(ParsedTokens.UNKNOWN, to)
        change_all_children(child, replace_dict)


def parse_param_re(match):
    parts = match.groups()
    return parts[0] + parse_param(parts[1])


def parse_param(st):
    if not st[1:-1].strip():
        return '()'
    parts = st[1:-1].split(',')
    prev_typ = res = ""
    for part in parts:
        part = part.strip().split()
        if len(part) == 1:
            res += prev_typ + ' ' + part[0]
        else:
            res += ' '.join(part)
            prev_typ = part[0]
        res += ', '
    return f"({res.removesuffix(', ')})"


def get_all_var_names(node):
    res = []
    res.extend(node.declared_vars)
    while node.parent:
        node = node.parent
        node = move_up_tree_while(node, lambda n: n.value.type != ParsedTokens.PROGRAM)
        res.extend(node.declared_vars)
    return res


def insert_function(node):
    child = node.children.pop(0)
    typ, name = child.value
    match typ:
        case ParsedTokens.QUESTION_MARK:
            if name == '()':
                return f"{extension_class}.ShortTryFunction(()=>{eval_tree(node)}"
            elif name == '[]':
                return f"{extension_class}.TryGetArr({eval_tree(node)}"
            else:
                raise Exception("Unknown question mak position")
        case ParsedTokens.DOUBLE_QUESTION_MARK:
            return f"{extension_class}.ShortTryFunctionNull(()=>{eval_tree(node)}"
        case ParsedTokens.EXCLAMATION_MARK:
            return f"{extension_class}.DoVoidAndReturn(ref {eval_tree(node.children[-2])}, ()=>{eval_tree(node)}"
        case ParsedTokens.DOLLAR:
            ref = eval_tree(node.children[-2])
            return f"{extension_class}.DoAndAssignVal(ref {ref}, ({ref})=>{eval_tree(node)}"
    node.children.insert(0, child)
    return False


def close_function(node):
    if node.children[0].value.type == ParsedTokens.CLOSE_QUESTION_MARK:
        popped = node.children.pop(0).value.name
        match popped:
            case '()':  # 3 short try catch on func
                return f"{eval_tree(node)})"
            case '[]':  # 3 short bounds check
                return f", {eval_tree(node)[1:-1]})"
    return False

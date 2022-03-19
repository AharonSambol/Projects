import math
import re
from enum import Enum, auto
from Tree import Tree
from collections import namedtuple


class Tokens(Enum):
    INDEX = auto()
    LIST = auto()
    COMMA = auto()
    NEW_LINE = auto()
    INT_CONSTANT = auto()
    FLOAT_CONSTANT = auto()
    BOOL_CONSTANT = auto()
    STR_CONSTANT = auto()
    MATH_OPERATOR = auto()
    BOOL_OPERATOR = auto()
    BRACKETS = auto()
    REMOVE_NULL = auto()
    LOOP = auto()
    CONDITION = auto()
    IN = auto()
    CONTROL_MODIFIER = auto()
    TAG = auto()
    SPECIAL_CHAR = auto()
    RANGE = auto()
    SHORT_SHORT_IF = auto()
    SHORT_NULL_IF = auto()
    SHORT_SHORT_NULL_IF = auto()
    SHORT_ELSE = auto()
    SWITCH = auto()
    CASE = auto()
    THROW_AWAY = auto()
    SWITCH_RETURN = auto()
    CLASS_TYPE = auto()
    CLASS_PARTS = auto()
    GET_SET = auto()
    OVERRIDE = auto()
    CAST = auto()
    CONST = auto()
    TRY_CATCH_FINALLY = auto()
    THROW = auto()
    ASSIGNMENT = auto()
    OTHER = auto()


class ParsedTokens(Enum):
    FUNCTION = auto()
    CONTROL_MODIFIER = auto()
    INDEX = auto()
    LIST = auto()
    CONST = auto()
    CONDITION_STATEMENT = auto()
    TYPE = auto()
    NAME = auto()
    ASSIGNMENT = auto()
    VAR_DECLARATION = auto()
    MULTIPLICATION = auto()
    DIVISION = auto()
    FLOOR_DIVISION = auto()
    CEILING_DIVISION = auto()
    ADDITION = auto()
    SUBTRACTION = auto()
    MODULO = auto()
    POW = auto()
    PARENTHESES = auto()
    BOOL_AND = auto()
    BOOL_OR = auto()
    BOOL_NOT = auto()
    BOOL_EQ = auto()
    BOOL_NEQ = auto()
    BOOL_SEQ = auto()
    BOOL_LEQ = auto()
    BOOL_L = auto()
    BOOL_S = auto()
    INT = auto()
    FLOAT = auto()
    STR = auto()
    BOOL = auto()
    PROGRAM = auto()
    UNKNOWN = auto()


Token = namedtuple('Token', ['type', 'name'])


def get_precedence(token):
    if token is None:
        return 0
    match token.type:
        case ParsedTokens.MODULO | ParsedTokens.MULTIPLICATION | ParsedTokens.DIVISION | \
             ParsedTokens.CEILING_DIVISION | ParsedTokens.FLOOR_DIVISION:
            return 60
        case ParsedTokens.ADDITION | ParsedTokens.SUBTRACTION:
            return 50
        case ParsedTokens.PARENTHESES:
            return 5
        case ParsedTokens.POW:
            return 70
        case ParsedTokens.BOOL_OR:
            return 11
        case ParsedTokens.BOOL_AND:
            return 10
        case ParsedTokens.BOOL_NOT:
            return 100
        case ParsedTokens.BOOL_EQ | ParsedTokens.BOOL_NEQ:
            return 20
        case ParsedTokens.BOOL_SEQ | ParsedTokens.BOOL_LEQ | ParsedTokens.BOOL_S | ParsedTokens.BOOL_L:
            return 30
        case _:
            return 1


def move_up_tree_while(node, func):
    while node.parent and func(node):
        node = node.parent
    return node


def parser(tokens):
    tokens.append(Token(Tokens.NEW_LINE, None))
    node = tree = Tree(Token(ParsedTokens.PROGRAM, None), None)
    line_num = 0
    for token in tokens:
        match token.type:
            case Tokens.NEW_LINE:
                line_num += 1
                if node.value.type == ParsedTokens.UNKNOWN and node.parent.value.type == ParsedTokens.UNKNOWN:
                    new_node = Tree(Token(ParsedTokens.ASSIGNMENT, token.name), node)
                    name = node.value.name
                    new_node.children.append(Tree(Token(ParsedTokens.TYPE, node.parent.value.name), new_node))
                    new_node.children.append(Tree(Token(ParsedTokens.NAME, name), new_node))
                    node.parent.parent.children[-1] = new_node
                node = move_up_tree_while(node, lambda n: n.value.type != ParsedTokens.PROGRAM)
            case Tokens.MATH_OPERATOR | Tokens.BOOL_OPERATOR:
                new_node_val = Token(symbol_to_token[token.name], token.name)
                node = move_up_tree_while(node, lambda n: get_precedence(n.value) >= get_precedence(new_node_val))
                if len(node.children) == 0:     # 3 var name
                    node = node.parent
                new_node = Tree(new_node_val, node)
                if token.name == 'not':
                    node.children.append(new_node)
                    node = new_node
                    continue

                new_node.children.append(node.children[-1])
                new_node.children[-1].parent = new_node
                node.children[-1] = new_node
                node = new_node
            case Tokens.BRACKETS | Tokens.LIST | Tokens.INDEX:
                if token.name in ['(', '[', '{']:
                    typ = {
                        '(': ParsedTokens.PARENTHESES,
                        '[': None,
                        '{': ParsedTokens.PROGRAM}[token.name]
                    if token.name == '{':
                        # 6 if prev is a function set its token to a function
                        if node.value.type == ParsedTokens.UNKNOWN and len(node.children) == 1 and \
                                node.children[0].value.type == ParsedTokens.PARENTHESES:
                            node = make_function(node)

                        node = move_up_tree_while(node, lambda n: n.value.type not in [
                            ParsedTokens.CONDITION_STATEMENT,
                            ParsedTokens.FUNCTION,
                            # 6 anything with curly braces!!!
                        ])
                    if token.name == '[':
                        typ = ParsedTokens.LIST if token.type == Tokens.LIST else ParsedTokens.INDEX
                    node = add_new(node, Token(None, None), typ)
                elif token.name in [')', ']', '}']:
                    typ = {
                        ')': [ParsedTokens.PARENTHESES],
                        ']': [ParsedTokens.LIST, ParsedTokens.INDEX],
                        '}': [ParsedTokens.PROGRAM, ParsedTokens.FUNCTION]}[token.name]
                    node = move_up_tree_while(node, lambda n: n.value.type not in typ).parent
                    if token.name == '}' and node.value.type == ParsedTokens.CONDITION_STATEMENT:
                        node = node.parent
            case Tokens.BOOL_CONSTANT | Tokens.STR_CONSTANT | Tokens.FLOAT_CONSTANT | Tokens.INT_CONSTANT:
                new_node = Tree(Token(const_to_const[token.type], token.name), node)
                node.children.append(new_node)
            case Tokens.ASSIGNMENT:
                # todo clean this mess up
                new_node = Tree(Token(ParsedTokens.ASSIGNMENT, token.name), node)
                node = node.parent
                name = node.children.pop(-1).value.name
                if node.value.type != ParsedTokens.PROGRAM:
                    node.parent.children.pop(-1)
                    typ = node.value.name
                    node = node.parent
                    if node.value.type == ParsedTokens.CONST:
                        node.parent.children.pop(-1)
                        typ = 'const ' + typ
                        node = node.parent
                    new_node.children.append(Tree(Token(ParsedTokens.TYPE, typ), new_node))
                new_node.children.append(Tree(Token(ParsedTokens.NAME, name), new_node))
                node.children.append(new_node)
                node = new_node
            case Tokens.CONTROL_MODIFIER:
                node = add_new(node, token, ParsedTokens.CONTROL_MODIFIER)
            case Tokens.COMMA:
                stop_at = {ParsedTokens.LIST, ParsedTokens.INDEX, ParsedTokens.PARENTHESES, ParsedTokens.PROGRAM}
                node = move_up_tree_while(node, lambda n: n.value.type not in stop_at)
            case Tokens.CONDITION:
                node = add_new(node, token, ParsedTokens.CONDITION_STATEMENT)
            case Tokens.CONST:
                node = add_new(node, token, ParsedTokens.CONST)
            case Tokens.OTHER:
                node = add_new(node, token, ParsedTokens.UNKNOWN)
            case _:
                print(f"UNSUPPORTED TYPE: { token.type }")
                exit(9)
    print("res:")
    eval_tree(tree)
    for n in tree.children:
        print(n.value)
    return tree


def make_function(node):
    func_node = Tree(Token(ParsedTokens.FUNCTION, node.value.name), None)
    child = node.children.pop(-1)
    node = node.parent
    if node.value.type == ParsedTokens.UNKNOWN:
        return_types = ", ".join(x.value.name for x in node.parent.children)
        func_node.children.append(Tree(Token(ParsedTokens.TYPE, return_types.strip()), func_node))
        node = node.parent
    func_node.parent = node
    node.children = [func_node]

    func_node.children.append(child)
    child.parent = func_node
    node = func_node
    return node


def add_new(node, token, typ):
    new_node = Tree(Token(typ, token.name), node)
    node.children.append(new_node)
    node = new_node
    return node


loop_var_name = 10000
const_to_const = {
    Tokens.BOOL_CONSTANT: ParsedTokens.BOOL,
    Tokens.STR_CONSTANT: ParsedTokens.STR,
    Tokens.FLOAT_CONSTANT: ParsedTokens.FLOAT,
    Tokens.INT_CONSTANT: ParsedTokens.INT,
}
token_to_symbol = {
    ParsedTokens.MODULO: '%',
    ParsedTokens.MULTIPLICATION: '*',
    ParsedTokens.DIVISION: '/',
    ParsedTokens.ADDITION: '+',
    ParsedTokens.SUBTRACTION: '-',
    ParsedTokens.BOOL_OR: '||',
    ParsedTokens.BOOL_AND: '&&',
    ParsedTokens.BOOL_EQ: '==',
    ParsedTokens.BOOL_NEQ: '!=',
    ParsedTokens.BOOL_SEQ: '<=',
    ParsedTokens.BOOL_LEQ: '>=',
    ParsedTokens.BOOL_S: '<',
    ParsedTokens.BOOL_L: '>',
    ParsedTokens.BOOL_NOT: '!',
}
symbol_to_token = {
    '+': ParsedTokens.ADDITION,
    '-': ParsedTokens.SUBTRACTION,
    '*': ParsedTokens.MULTIPLICATION,
    '/': ParsedTokens.DIVISION,
    '//': ParsedTokens.FLOOR_DIVISION,
    '^': ParsedTokens.POW,
    '%': ParsedTokens.MODULO,
    'or': ParsedTokens.BOOL_OR,
    'and': ParsedTokens.BOOL_AND,
    '==': ParsedTokens.BOOL_EQ,
    '!=': ParsedTokens.BOOL_NEQ,
    '<=': ParsedTokens.BOOL_SEQ,
    '>=': ParsedTokens.BOOL_LEQ,
    '<': ParsedTokens.BOOL_S,
    '>': ParsedTokens.BOOL_L,
    'not': ParsedTokens.BOOL_NOT,
}


def eval_tree(node):
    match node.value.type:
        case ParsedTokens.PROGRAM:
            res = ""
            for n in node.children:
                n.value = f"{ eval_tree(n) }"
                if not n.value.endswith('}'):
                    n.value += ';'
                res += n.value + '\n'
            return f"{{\n{ res }\n}}"
        case ParsedTokens.MODULO | ParsedTokens.MULTIPLICATION | ParsedTokens.DIVISION | ParsedTokens.ADDITION \
             | ParsedTokens.SUBTRACTION | ParsedTokens.BOOL_OR | ParsedTokens.BOOL_AND | ParsedTokens.BOOL_EQ \
             | ParsedTokens.BOOL_NEQ | ParsedTokens.BOOL_SEQ | ParsedTokens.BOOL_LEQ | ParsedTokens.BOOL_S \
             | ParsedTokens.BOOL_L:
            return f"{eval_tree(node.children[0])} { token_to_symbol[node.value.type] } {eval_tree(node.children[1])}"
        case ParsedTokens.CEILING_DIVISION:
            return f"((int)Math.Ceiling((double){eval_tree(node.children[0])}/(double){eval_tree(node.children[1])}))"
        case ParsedTokens.FLOOR_DIVISION:
            return f"Math.Floor({eval_tree(node.children[0])}, {eval_tree(node.children[1])})"
        case ParsedTokens.PARENTHESES | ParsedTokens.INDEX | ParsedTokens.LIST:
            res = ""
            for i, child in enumerate(node.children):
                res += str(eval_tree(child))
                if i + 1 != len(node.children):
                    res += ', '
            if node.value.type == ParsedTokens.PARENTHESES:
                return f"( { res } )"
            if node.value.type == ParsedTokens.INDEX:
                return f"[ {res} ]"
            if re.match(r'-\w+-', res):
                return f"new { res[1:-1] }[0]"
            if res == "":
                print("NEED TO FIGURE OUT TYP")
                exit(9)
                # 6 return f"new {typ}[0]"
            return f"new[]{{ { res } }}"
        case ParsedTokens.POW:
            return f"Math.Pow({eval_tree(node.children[0])}, {eval_tree(node.children[1])})"
        case ParsedTokens.BOOL_NOT:
            return f"!{eval_tree(node.children[0])}"
        case ParsedTokens.INT | ParsedTokens.FLOAT:
            return node.value.name
        case ParsedTokens.STR:
            return f'"{ node.value.name }"'
        case ParsedTokens.BOOL:
            return 'true' if node.value.name else 'false'
        case ParsedTokens.ASSIGNMENT:
            if node.children[0].value.type == ParsedTokens.NAME:
                res = 'var '
            else:
                typ = node.children.pop(0).value.name
                typ = re.sub(r'\bstr\b', 'string', typ)
                if typ == 'const':
                    typ = 'const var'
                res = typ + " "
            res += node.children.pop(0).value.name
            if len(node.children) == 0:
                return res
            return f"{ res } = { eval_tree(node.children[0]) }"
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
                dependencies.add("System.Linq")
                global loop_var_name

                loop_var_name += 1
                # 2 while re.search(r'\b_____' + str(loop_var_name) + r'\b', code_str):
                # 2    loop_var_name += 1
                return f"foreach(var _____{loop_var_name} in Enumerable.Range(0, {eval_tree(cond)})) {eval_tree(block)}"
            if name == 'elif':
                name = 'else if'
            return f"{name} ({eval_tree(cond)}) {eval_tree(block)}"
        case ParsedTokens.CONTROL_MODIFIER:
            match node.value.name:
                case 'return':
                    return f"return { eval_tree(node.children[0]) }"
                case 'break':
                    pass
                case 'continue':
                    pass
                case 'rewind':
                    pass
                case 'restart':
                    pass
        case ParsedTokens.FUNCTION:
            if len(node.children) == 3:
                return_types = node.children.pop(0).value.name
                return_types = re.sub(r'\bstr\b', 'string', return_types)
                if ',' in return_types:
                    return_types = f"({ return_types })"
            else:
                return_types = "void"
            # 3 flatten input variables:
            prev_type = ""
            for n in node.children[0].children:
                if n.children:
                    prev_type = n.value.name if n.value.name != 'str' else 'string'
                    n.value = Token(n.value.type, prev_type + ' ' + n.children[0].value.name)
                else:
                    n.value = Token(n.value.type, prev_type + ' ' + n.value.name)
            return f"public { return_types } { node.value.name } { eval_tree(node.children[0]) } " \
                   f"{ eval_tree(node.children[1]) }"
        case ParsedTokens.UNKNOWN:
            return node.value.name
        case _:
            pass


dependencies = set()    # todo add at top of file
parser([
    # Token(Tokens.BRACKETS, '('), Token(Tokens.INT_CONSTANT, 5), Token(Tokens.BOOL_OPERATOR, '+'),
    # Token(Tokens.INT_CONSTANT, 3), Token(Tokens.MATH_OPERATOR, '*'),
    # Token(Tokens.BOOL_OPERATOR, 'not'),
    # Token(Tokens.BRACKETS, '('),
    # Token(Tokens.INT_CONSTANT, 6), Token(Tokens.BOOL_OPERATOR, '>='),  Token(Tokens.INT_CONSTANT, 5),
    # Token(Tokens.BRACKETS, ')'), Token(Tokens.BRACKETS, ')'), Token(Tokens.MATH_OPERATOR, '*'),
    # Token(Tokens.INT_CONSTANT, 7), Token(Tokens.MATH_OPERATOR, '//'), Token(Tokens.INT_CONSTANT, 11),
    # Token(Tokens.NEW_LINE, None),
    # Token(Tokens.OTHER, 'name'), Token(Tokens.ASSIGNMENT, '='), Token(Tokens.INT_CONSTANT, 5),
    # Token(Tokens.BOOL_OPERATOR, '+'), Token(Tokens.INT_CONSTANT, 3),
    # Token(Tokens.NEW_LINE, None),
    # Token(Tokens.FLOAT_CONSTANT, 1.543), Token(Tokens.MATH_OPERATOR, '+'), Token(Tokens.STR_CONSTANT, '2'),
    # Token(Tokens.MATH_OPERATOR, '+'), Token(Tokens.OTHER, 'name'),
    # Token(Tokens.NEW_LINE, None),
    # Token(Tokens.INT_CONSTANT, 6666), Token(Tokens.MATH_OPERATOR, '%'), Token(Tokens.INT_CONSTANT, 4),
    # Token(Tokens.NEW_LINE, None), Token(Tokens.OTHER, 'char'), Token(Tokens.OTHER, 'v'),

    # Token(Tokens.NEW_LINE, None), Token(Tokens.CONDITION, 'until'), Token(Tokens.OTHER, 'x'),
    # Token(Tokens.BOOL_OPERATOR, '=='),  Token(Tokens.OTHER, 'x'),
    # Token(Tokens.BRACKETS, '{'),
    # Token(Tokens.OTHER, 'name'), Token(Tokens.ASSIGNMENT, '='), Token(Tokens.INT_CONSTANT, 5),
    # Token(Tokens.NEW_LINE, None),
    # Token(Tokens.CONST, 'const'), Token(Tokens.CONST, 'str'), Token(Tokens.OTHER, 'name2'),
    # Token(Tokens.ASSIGNMENT, '='), Token(Tokens.INT_CONSTANT, 5), Token(Tokens.NEW_LINE, None),
    # Token(Tokens.OTHER, 'break'),
    # Token(Tokens.BRACKETS, '}'), Token(Tokens.NEW_LINE, None),


    Token(Tokens.OTHER, "func"), Token(Tokens.BRACKETS, '('),
    Token(Tokens.BRACKETS, ')'), Token(Tokens.BRACKETS, '{'),
    Token(Tokens.NEW_LINE, None),
    Token(Tokens.OTHER, 'input'), Token(Tokens.MATH_OPERATOR, '+'),
    Token(Tokens.INT_CONSTANT, 5),
    Token(Tokens.NEW_LINE, None),
    Token(Tokens.CONTROL_MODIFIER, 'return'), Token(Tokens.OTHER, 'input'), Token(Tokens.MATH_OPERATOR, '+'),
    Token(Tokens.INT_CONSTANT, 1),
    Token(Tokens.NEW_LINE, None),
    Token(Tokens.BRACKETS, '}'),
])

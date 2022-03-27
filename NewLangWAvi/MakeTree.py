from HelperFunctions import *


def make_tree(tokens):
    in_list_comp = 0
    node = tree = Tree(Token(ParsedTokens.PROGRAM, None), None)
    line_num = 0
    for i, token in enumerate(tokens):
        print(token)
        node, in_list_comp = parse_token(in_list_comp, line_num, node, token)
    return tree


def parse_token(in_list_comp, line_num, node, token):
    match token.type:
        case Tokens.NEW_LINE:
            line_num += 1
            node = move_up_tree_while(node, lambda n: n.value.type != ParsedTokens.PROGRAM)
            node.children.append(Tree(Token(ParsedTokens.NEW_LINE, '\n'), node))
        case Tokens.CLASS_TYPE:
            node = add_new(node, token, ParsedTokens.CLASS_TYPE)
        case Tokens.CLASS_PARTS:
            node = add_new(node, token, ParsedTokens.CLASS_PARTS)
        case Tokens.NEGATIVE:
            new_node = Tree(Token(ParsedTokens.NEGATIVE, token.name), node)
            node.children.append(new_node)
            node = new_node
        case Tokens.MATH_OPERATOR | Tokens.BOOL_OPERATOR:
            new_node_val = Token(symbol_to_token[token.name], token.name)
            node = move_up_tree_while(node, lambda n: get_precedence(n.value) >= get_precedence(new_node_val))
            if len(node.children) == 0 and token.name != 'not':  # 3 var name
                node = node.parent
            new_node = Tree(new_node_val, node)
            if token.name == 'not':
                node.children.append(new_node)
                node = new_node
            else:
                new_node.children.append(node.children[-1])
                new_node.children[-1].parent = new_node
                node.children[-1] = new_node
                node = new_node
        case Tokens.DICT | Tokens.SET:
            typ = {Tokens.DICT: ParsedTokens.DICT, Tokens.SET: ParsedTokens.SET}[token.type]
            if token.name == '{':
                node = add_new(node, token, typ)
            else:
                node = move_up_tree_while(node, lambda n: n.value.type != typ).parent
        case Tokens.BRACKETS:
            if token.name == '(':
                node = add_new(node, token, ParsedTokens.PARENTHESES)
            else:
                node = move_up_tree_while(node, lambda n: n.value.type != ParsedTokens.PARENTHESES).parent
        case Tokens.BRACES:
            if token.name == '{':
                if node.value.type == ParsedTokens.UNKNOWN and len(node.children) == 1 and \
                        node.children[0].value.type == ParsedTokens.PARENTHESES and \
                        (node.parent.value.type == ParsedTokens.PROGRAM or
                         node.parent.value.type == ParsedTokens.UNKNOWN and
                         node.parent.parent.value.type == ParsedTokens.PROGRAM):
                    node = make_function(node)
                # 1 do i need this?
                node = move_up_tree_while(node, lambda n: n.value.type not in [
                    ParsedTokens.CONDITION_STATEMENT,
                    ParsedTokens.FUNCTION,
                    ParsedTokens.FOR_LOOP,
                    ParsedTokens.CLASS_TYPE,
                    ParsedTokens.CLASS_PARTS,
                    ParsedTokens.TRY_CATCH_FINALLY,
                    # 6 anything with curly braces!!!
                ])
                node = add_new(node, token, ParsedTokens.PROGRAM)
            else:
                node = move_up_tree_while(node, lambda n: n.value.type not in [
                    ParsedTokens.PROGRAM, ParsedTokens.FUNCTION
                ]).parent
                if node.value.type in [ParsedTokens.CONDITION_STATEMENT, ParsedTokens.FOR_LOOP]:
                    node = node.parent
        case Tokens.LIST | Tokens.INDEX | Tokens.LIST_COMPREHENSION:
            if token.type == Tokens.LIST_COMPREHENSION:
                in_list_comp += 1 if token.name == '[' else -1
            if token.name == '[':
                typ = {
                    Tokens.LIST: ParsedTokens.LIST,
                    Tokens.INDEX: ParsedTokens.INDEX,
                    Tokens.LIST_COMPREHENSION: ParsedTokens.LIST_COMPREHENSION
                }[token.type]
                node = add_new(node, token, typ)
            else:
                typ = [ParsedTokens.LIST, ParsedTokens.INDEX, ParsedTokens.LIST_COMPREHENSION, ParsedTokens.DOT_DOT]
                node = move_up_tree_while(node, lambda n: n.value.type not in typ).parent
        case Tokens.BOOL_CONSTANT | Tokens.STR_CONSTANT | Tokens.FLOAT_CONSTANT | Tokens.INT_CONSTANT | \
             Tokens.NULL_CONSTANT:
            new_node = Tree(Token(const_to_const[token.type], token.name), node)
            node.children.append(new_node)
        case Tokens.ASSIGNMENT:
            new_node = Tree(Token(ParsedTokens.ASSIGNMENT, token.name), None)
            node = node.parent
            node = move_up_tree_while(node, lambda n: n.value.type != ParsedTokens.PROGRAM)
            name = node.children.pop()
            # name.value = Token(ParsedTokens.NAME, name.value.name)
            if node.value.type != ParsedTokens.PROGRAM:
                node.parent.children.pop()
                typ = node.value.name
                node = node.parent
                if node.value.type == ParsedTokens.CONST:
                    node.parent.children.pop()
                    typ = 'const ' + typ
                    node = node.parent
                new_node.children.append(Tree(Token(ParsedTokens.TYPE, typ), new_node))
            new_node.children.append(name)
            name.parent = new_node
            node.children.append(new_node)
            new_node.parent = node
            node = new_node
        case Tokens.CONTROL_MODIFIER:
            node = add_new(node, token, ParsedTokens.CONTROL_MODIFIER)
        case Tokens.COMMA:
            node = move_to_comma_pos(node)
        case Tokens.COLON:
            node = move_to_comma_pos(node)
            add_new(node, token, ParsedTokens.COLON)
        case Tokens.DOT:
            new_node = Tree(Token(ParsedTokens.DOT, token.name), node.parent)
            new_node.children.append(node)
            node.parent.children[-1] = new_node
            new_node.children[-1].parent = new_node
            node = new_node
        case Tokens.CONDITION:
            if in_list_comp:
                node = move_up_tree_while(node, lambda n: n.value.type != ParsedTokens.LIST_COMPREHENSION)
            node = add_new(node, token, ParsedTokens.CONDITION_STATEMENT)
        case Tokens.LOOP:
            if in_list_comp:
                node = move_up_tree_while(node, lambda n: n.value.type != ParsedTokens.LIST_COMPREHENSION)
            node = add_new(node, token, ParsedTokens.FOR_LOOP)
        case Tokens.IN | Tokens.INDEX_KEYWORD:
            new_node = move_to_comma_pos(node)
            if new_node.value.type == ParsedTokens.FOR_LOOP:
                node = new_node
                add_new(node, token, ParsedTokens.IN if token.type == Tokens.IN else ParsedTokens.INDEX_KEYWORD)
            elif token.type == Tokens.INDEX:
                raise Exception("'index' keyword must be in for loop")
            else:
                return parse_token(in_list_comp, line_num, node, Token(Tokens.BOOL_OPERATOR, 'in'))
        case Tokens.EXCLAMATION_MARK | Tokens.QUESTION_MARK | Tokens.DOUBLE_QUESTION_MARK | Tokens.REMOVE_NULL:
            if node.value.type in [ParsedTokens.PARENTHESES, ParsedTokens.INDEX] or \
                    token.type == Tokens.REMOVE_NULL:
                # 3 short try catch on function \ short check bounds
                if node.value.type in [ParsedTokens.PARENTHESES, ParsedTokens.INDEX]:
                    n = node.parent
                else:
                    n = node
                while n.parent and n.parent.value.type in [
                    ParsedTokens.DOT,
                ]:
                    n = n.parent
                if token.type == Tokens.REMOVE_NULL:
                    n = n.parent
                    remove_null_node = Tree(Token(ParsedTokens.REMOVE_NULL_DEFAULT, None), n)
                    node = remove_null_node
                    remove_null_node.children = [n.children.pop()]
                    remove_null_node.children[0].parent = remove_null_node
                    n.children.append(remove_null_node)
                else:
                    val = {
                        ParsedTokens.PARENTHESES: '()',
                        ParsedTokens.INDEX: '[]',
                    }[node.value.type]

                    typ = {
                        Tokens.DOUBLE_QUESTION_MARK: ParsedTokens.DOUBLE_QUESTION_MARK,
                        Tokens.QUESTION_MARK: ParsedTokens.QUESTION_MARK,
                        Tokens.EXCLAMATION_MARK: ParsedTokens.EXCLAMATION_MARK,
                    }[token.type]

                    # 2 in order to open '...('
                    n.children.insert(0, Tree(Token(typ, val), node))
                    # 2 in order to close ')'
                    node.children.insert(0, Tree(Token(ParsedTokens.CLOSE_QUESTION_MARK, val), node))
        case Tokens.TAG:
            loop = node.parent
            goto = Tree(Token(ParsedTokens.GO_TO, token.name), loop.parent)
            loop.parent.children[-1] = goto
            goto.children.append(loop)
            loop.parent = goto
        case Tokens.DOT_DOT:
            node = move_up_tree_while(node, lambda n: n.value.type != ParsedTokens.LIST)
            child = node.children.pop()
            parent = node.parent
            if len(node.children) == 0:
                node.parent.children.pop()
            node = add_new(parent, token, ParsedTokens.DOT_DOT)
            node.children.append(child)
            child.parent = node
        case Tokens.PIPE:
            node = move_to_comma_pos(node)
            add_new(node, token, ParsedTokens.PIPE)
        case Tokens.CONST:
            node = add_new(node, token, ParsedTokens.CONST)
        case Tokens.OTHER:
            node = add_new(node, token, ParsedTokens.UNKNOWN)
        case Tokens.TRY_CATCH_FINALLY:
            if token.name in ['fix', 'finally']:
                node = move_up_tree_while(node, lambda n: n.value.type != ParsedTokens.TRY_CATCH_FINALLY).parent
            node = add_new(node, token, ParsedTokens.TRY_CATCH_FINALLY)
        case Tokens.THROW:
            node = add_new(node, token, ParsedTokens.THROW)
        case Tokens.PLUS_PLUS:  # 6 doesnt work if ++ is before the variable
            prec = get_precedence(Token(ParsedTokens.PLUS_PLUS, ''))
            node = move_up_tree_while(node, lambda n: get_precedence(n.value) >= prec)
            child = node.children.pop()
            new = add_new(node, token, ParsedTokens.PLUS_PLUS)
            child.parent = new
            new.children.append(child)
            node = new.parent
        case Tokens.SPECIAL_CHAR:
            if token.name == '@':
                node = add_new(node, token, ParsedTokens.UNKNOWN)
            else:
                raise Exception(f"Unsupported type: {token.type}")
        case _:
            raise Exception(f"Unsupported type: {token.type}")
    return node, in_list_comp


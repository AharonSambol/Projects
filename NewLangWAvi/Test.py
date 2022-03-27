from Parser import parser

# 5 new DataStructure<int>(){1,2,3,4,5,6}
# 3 enumerate(zip())

parser("""
print(4+5.1)
""")

# parser([
# Token(Tokens.BRACKETS, '('), Token(Tokens.INT_CONSTANT, 5), Token(Tokens.BOOL_OPERATOR, '+'),
# Token(Tokens.INT_CONSTANT, 3), Token(Tokens.MATH_OPERATOR, '*'),
# Token(Tokens.BOOL_OPERATOR, 'not'),
# Token(Tokens.BRACKETS, '('),
# Token(Tokens.INT_CONSTANT, 6), Token(Tokens.BOOL_OPERATOR, '>='),  Token(Tokens.INT_CONSTANT, 5),
# Token(Tokens.BRACKETS, ')'), Token(Tokens.BRACKETS, ')'), Token(Tokens.MATH_OPERATOR, '*'),
# Token(Tokens.INT_CONSTANT, 7), Token(Tokens.MATH_OPERATOR, '//'), Token(Tokens.INT_CONSTANT, 11),
# Token(Tokens.NEW_LINE, None),
# Token(Tokens.OTHER, 'name'), Token(Tokens.ASSIGNMENT, '+='), Token(Tokens.INT_CONSTANT, 5),
# Token(Tokens.BOOL_OPERATOR, '+'), Token(Tokens.INT_CONSTANT, 3),
# Token(Tokens.NEW_LINE, None),
# Token(Tokens.FLOAT_CONSTANT, 1.543), Token(Tokens.MATH_OPERATOR, '+'), Token(Tokens.STR_CONSTANT, '2'),
# Token(Tokens.MATH_OPERATOR, '+'), Token(Tokens.OTHER, 'name'),
# Token(Tokens.NEW_LINE, None),
# Token(Tokens.INT_CONSTANT, 6666), Token(Tokens.MATH_OPERATOR, '%'), Token(Tokens.INT_CONSTANT, 4),
# Token(Tokens.NEW_LINE, None),
# Token(Tokens.OTHER, 'char'), Token(Tokens.OTHER, 'v'),
#
# Token(Tokens.NEW_LINE, None),
#
# Token(Tokens.CONDITION, 'until'), Token(Tokens.OTHER, 'x'),
# Token(Tokens.BOOL_OPERATOR, '=='),  Token(Tokens.OTHER, 'x'),
# Token(Tokens.BRACKETS, '{'), Token(Tokens.NEW_LINE, None),
# Token(Tokens.OTHER, 'name'), Token(Tokens.ASSIGNMENT, '='), Token(Tokens.INT_CONSTANT, 5),
# Token(Tokens.NEW_LINE, None),
# Token(Tokens.CONST, 'const'), Token(Tokens.CONST, 'str'), Token(Tokens.OTHER, 'name2'),
# Token(Tokens.ASSIGNMENT, '='), Token(Tokens.INT_CONSTANT, 5), Token(Tokens.NEW_LINE, None),
# Token(Tokens.CONTROL_MODIFIER, 'break'),
# Token(Tokens.BRACKETS, '}'),
#
# Token(Tokens.NEW_LINE, None),
#
# Token(Tokens.OTHER, "int"), Token(Tokens.COMMA, ","), Token(Tokens.OTHER, "int"), Token(Tokens.OTHER, "func"),
# Token(Tokens.BRACKETS, '('), # Token(Tokens.OTHER, 'extend'),
# Token(Tokens.OTHER, 'int'), Token(Tokens.OTHER, 'name'),
# Token(Tokens.COMMA, ','), Token(Tokens.OTHER, 'name2'),
# Token(Tokens.BRACKETS, ')'), Token(Tokens.BRACKETS, '{'),
# Token(Tokens.NEW_LINE, None),
# Token(Tokens.OTHER, 'input'), Token(Tokens.MATH_OPERATOR, '+'),
# Token(Tokens.INT_CONSTANT, 5),
# Token(Tokens.NEW_LINE, None),
# Token(Tokens.CONTROL_MODIFIER, 'return'), Token(Tokens.OTHER, 'input'), Token(Tokens.MATH_OPERATOR, '+'),
# Token(Tokens.INT_CONSTANT, 1),
# Token(Tokens.NEW_LINE, None),
# Token(Tokens.BRACKETS, '}'),
#
# Token(Tokens.NEW_LINE, None),
#
# Token(Tokens.LOOP, "for"), Token(Tokens.OTHER, "i"),
# Token(Tokens.INDEX_KEYWORD, "index"), Token(Tokens.OTHER, "arr"),
# Token(Tokens.BRACKETS, '{'), Token(Tokens.NEW_LINE, None),
# Token(Tokens.OTHER, 'str?'), Token(Tokens.OTHER, 'name2'), Token(Tokens.ASSIGNMENT, '='),
# Token(Tokens.INT_CONSTANT, 5), Token(Tokens.NEW_LINE, None), Token(Tokens.BRACKETS, '}'),
#
# Token(Tokens.NEW_LINE, None),
#
# Token(Tokens.OTHER, 'first'), Token(Tokens.DOT, None), Token(Tokens.OTHER, 'second'), Token(Tokens.DOT, None),
# Token(Tokens.OTHER, 'func1'), Token(Tokens.BRACKETS, '('), Token(Tokens.QUESTION_MARK, '?'),
# Token(Tokens.INT_CONSTANT, 5), Token(Tokens.BRACKETS, ')'),
# Token(Tokens.INDEX, '['), Token(Tokens.QUESTION_MARK, None),
# Token(Tokens.INT_CONSTANT, 5), Token(Tokens.INDEX, ']'), Token(Tokens.REMOVE_NULL, '-?'),
# Token(Tokens.OTHER, 'z'),
#
# Token(Tokens.NEW_LINE, None),
#
# Token(Tokens.LIST, '['), Token(Tokens.OTHER, '-int-'), Token(Tokens.LIST, ']'),
#
# Token(Tokens.NEW_LINE, None),
#
# Token(Tokens.LOOP, "for"), Token(Tokens.OTHER, "i"),
# Token(Tokens.INDEX_KEYWORD, "index"), Token(Tokens.OTHER, "arr"),
# Token(Tokens.BRACKETS, '{'), Token(Tokens.TAG, 'loop1'),
# Token(Tokens.NEW_LINE, None),
# Token(Tokens.CONTROL_MODIFIER, 'break'), Token(Tokens.OTHER, 'loop1'),
# Token(Tokens.BRACKETS, '}'),

# Token(Tokens.OTHER, 'x'), Token(Tokens.ASSIGNMENT, '='), Token(Tokens.OTHER, 'y'),
# Token(Tokens.REMOVE_NULL, '-?'),
# Token(Tokens.OTHER, 'z'),
# Token(Tokens.REMOVE_NULL, '-?'),
# Token(Tokens.OTHER, 'f'),

# Token(Tokens.LIST_COMPREHENSION, '['),
# Token(Tokens.OTHER, 'x'), Token(Tokens.MATH_OPERATOR, '+'), Token(Tokens.INT_CONSTANT, '1'),
# Token(Tokens.LOOP, 'for'), Token(Tokens.OTHER, 'x'), Token(Tokens.IN, 'in'), Token(Tokens.OTHER, 'arr'),
# Token(Tokens.CONDITION, 'if'), Token(Tokens.OTHER, 'x'), Token(Tokens.MATH_OPERATOR, '%'),
# Token(Tokens.INT_CONSTANT, '2'), Token(Tokens.BOOL_OPERATOR, '=='), Token(Tokens.INT_CONSTANT, '0'),
# Token(Tokens.LIST_COMPREHENSION, ']'),

# Token(Tokens.LIST, '['), Token(Tokens.INT_CONSTANT, '2'), Token(Tokens.DOT_DOT, '..'), Token(Tokens.OTHER, 'x'),
# Token(Tokens.LIST, ']'), Token(Tokens.MATH_OPERATOR, '+'), Token(Tokens.LIST, '['),
# Token(Tokens.INT_CONSTANT, '2'), Token(Tokens.COMMA, ','), Token(Tokens.OTHER, 'x'),
# Token(Tokens.LIST, ']'),
# ])

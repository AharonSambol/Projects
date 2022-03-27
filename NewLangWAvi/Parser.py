import re

from MakeTree import make_tree
from HelperFunctions import *
from ParseTree import eval_tree, change_all_children
from Tokenizer import tokenize
from ParseTree import extension_methods


def parser(input_code):
    tokens = tokenize(input_code)
    if tokens and tokens[-1].type != Tokens.NEW_LINE:
        tokens.append(Token(Tokens.NEW_LINE, None))
    tree = make_tree(tokens)

    global extension_class

    # 2 while extension_class in res:
    # 2     extension_class += "_"
    change_all_children(tree,
                        {
                            'Enum': (f'{ extension_class }.Enumerate', False),
                            'Zip': (f'{ extension_class }.Zip', False),
                            'Print': ('Console.WriteLine', False),
                            'Any': (f'{ extension_class }.Any', False),
                            'All': (f'{ extension_class }.All', False),
                            'Bool': (f'{ extension_class }.ToBool', False),
                            'Int': (f'int.Parse("" +', True),
                            'Float': (f'float.Parse("" +', True),
                            'Str': (f'("" +', True),

                        })

    eval_tree(tree)
    print("//imports:")
    for i in dependencies:
        print(f"using {i};")
    print("//res:")
    for n in tree.children:
        if isinstance(n.value, Token) and n.value.type == ParsedTokens.NEW_LINE:
            continue
        if n.value != ';':
            print(n.value)
    exit(9)
    print("//funcs:")
    print(f"public static class { extension_class }{{")
    for f in extension_methods:
        print(f)
    print('}')
    print("//classes:")
    for c in built_in_classes:
        print(c)
    return tree





# 2 replace string with @string?
# 2 int?[] a = new[]{1}     doesnt work!

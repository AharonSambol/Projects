import re
from colorama import Back, Style


class Print:
    def __init__(self, get_children, get_val, show_newline_literal=False, return_instead_of_print=False):
        # this is a lambda which returns a list of all the children
        # in order to support trees of different kinds eg:
        #   self.child_right, self.child_left... or
        #   self.children = []... or
        #   self.children = {}... or anything else
        self.get_children = get_children
        self.get_node_val = get_val
        # if true will display \n as \n and not as new lines
        self.show_newline = show_newline_literal
        self.dont_print = return_instead_of_print

    def __call__(self, node):
        res = self.tree_to_str(node)
        gray = lambda x: Back.LIGHTBLACK_EX + x + Style.RESET_ALL
        lines = ["".join(gray(x) if x.startswith('[') else x for x in line) for line in res]
        if self.dont_print:
            return "\n".join(lines)
        print("\n".join(lines))

    def get_val(self, node):
        st_val = str(self.get_node_val(node))

        if self.show_newline:
            def escape_enter(match):
                return '\\n' if match.group(0) == '\n' else '\\\\n'
            st_val = re.sub(r'(\n|\\n)', escape_enter, st_val)

        if '\n' not in st_val:
            return [[st_val]]

        lst_val = st_val.split("\n")
        longest = max(len(x) for x in lst_val)
        top, bottom = ['_' * (longest + 4)], ['-' * (longest + 4)]
        return top + [f'| {x}{" " * (longest - len(x))} |' for x in lst_val] + bottom

    def tree_to_str(self, node):
        val = self.get_val(node)

        if len(self.get_children(node)) == 0:
            if len(val) == 1:
                return [['[ ' + val[0][0] + ' ]']]
            return val

        to_print = [[]]
        len_row_1 = spacing = 0
        for child in self.get_children(node):
            to_print[0].append(' ' * (spacing - len_row_1) + '\\')
            len_row_1 = spacing + 1
            child_print = self.tree_to_str(child)
            for l, line in enumerate(child_print):
                if l + 1 >= len(to_print):
                    to_print.append([])
                to_print[l + 1].append(' ' * (spacing - len("".join(to_print[l + 1]))))
                to_print[l + 1].extend(line)
            spacing = max(len("".join(x)) for x in to_print) + 1

        to_print[0][0] = '|'
        spacing = (len_row_1 - len(val[0][0])) // 2
        spacing = spacing * ' '
        if len(val) == 1:
            val = [[f'[{ spacing }{val[0][0]}{ spacing }]']]
        to_print = val + to_print
        return to_print


# ---------- example: ----------
# class Tree:
#     def __init__(self, val):
#         self.val = val
#         self.children = []
# 
#     def add_child(self, child):
#         self.children.append(child)
#         return child
# 
# 
# class Person:
#     def __init__(self, age, name):
#         self.age = age
#         self.name = name
# 
#     def __str__(self):
#         return f"""Person {{ 
#     age: {self.age}, 
#     name: {self.name} 
# }}"""
# 
# 
# tree = Tree(0)
# r = tree.add_child(Tree([1, 2, 3]))
# l = tree.add_child(Tree({1: "qo", 24: " 5326"}))
# rl = r.add_child(Tree(43216))
# rr = r.add_child(Tree(Person(17, "Aharon")))
# rr.add_child(Tree(0))
# lr = l.add_child(Tree(5))
# lm = l.add_child(Tree("\n"))
# ll = l.add_child(Tree(6))
# rl.add_child(Tree("!!!!"))
# rlm = rl.add_child(Tree("!!!!\\n!!"))
# rl.add_child(Tree("!!!!!!"))
# rlm.add_child(Tree("looooong"))
# rlm.add_child(Tree("looooong"))
# pt = Print(lambda x: x.children, lambda x: x.val)
# pt(node=tree)

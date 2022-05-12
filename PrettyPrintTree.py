from colorama import Back, Style


class Print:
    def __init__(self, get_children):
        # this is a lambda which returns a list of all the children
        # in order to support trees of different kinds eg:
        #   self.child_right, self.child_left... or
        #   self.children = []... or
        #   self.children = {}... or anything else
        self.get_children = get_children

    def __call__(self, node):
        res = self.tree_to_str(node)
        gray = lambda x: Back.LIGHTBLACK_EX + x + Style.RESET_ALL
        lines = ["".join(gray(x) if x.startswith('[') else x for x in line) for line in res]
        print("\n".join(lines))

    def tree_to_str(self, node):
        if len(self.get_children(node)) == 0:
            return [[f"[ {node.val} ]"]]
        to_print = [
            [f" {node.val} "],
            []
        ]
        spacing = 0
        for child in self.get_children(node):
            to_print[1].append(" " * (spacing - len("".join(to_print[1]))) + '\\')
            child_print = self.tree_to_str(child)
            for l, line in enumerate(child_print):
                if l + 2 >= len(to_print):
                    to_print.append([])
                to_print[l + 2].append(" " * (spacing - len("".join(to_print[l + 2]))))
                to_print[l + 2].extend(line)
            spacing = max(len("".join(x)) for x in to_print) + 1

        to_print[1][0] = '|'
        spacing = (len("".join(to_print[1])) - len("".join(to_print[0])) - 2) // 2
        spacing = spacing * " "
        to_print[0][0] = '[' + spacing + to_print[0][0] + spacing + ']'
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
# tree = Tree(0)
# r = tree.add_child(Tree(1))
# l = tree.add_child(Tree(2))
# rr = r.add_child(Tree(3))
# rl = r.add_child(Tree(4))
# lr = l.add_child(Tree(5))
# lm = l.add_child(Tree(6))
# ll = l.add_child(Tree(7))
# rl.add_child(Tree(8))
# rlm = rl.add_child(Tree(9))
# rl.add_child(Tree(10))
# rlm.add_child(Tree(11))
# rlm.add_child(Tree(12))
# pt = Print(lambda x: x.children)
# pt(node=tree)

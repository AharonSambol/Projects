class Node:
    def __init__(self):
        self.pointers = []


class Pointer:
    def __init__(self, dest, path):
        self.dest, self.path = dest, path


def regex_divisible_by(n):
    nodes = make_graph(n)
    while len(nodes) > 1:
        node_to_rem = nodes[1]
        node_to_self = find_node_to_self(node_to_rem)
        for node in nodes:
            pointer_to_rem, pointers_to_add = None, []
            for i, pointer in enumerate(node.pointers):
                if pointer.dest == node_to_rem:
                    to = pointer.path
                    pointer_to_rem = i
                    for pointer2 in node_to_rem.pointers:
                        path = to + (f'({ node_to_self })*' if node_to_self is not None else '') + pointer2.path
                        pointers_to_add.append(Pointer(pointer2.dest, path))

            if pointer_to_rem is not None:
                node.pointers.pop(pointer_to_rem)
            for add in pointers_to_add:
                for pointer in node.pointers:   # check if already has pointer to that dest
                    if pointer.dest == add.dest:
                        pointer.path = f'(?:{ pointer.path }|{ add.path })'
                        break
                else:
                    node.pointers.append(add)
        nodes.pop(1)
    return f'^({ nodes[0].pointers[0].path })+$'


def find_node_to_self(node_to_rem):
    for i, pointer in enumerate(node_to_rem.pointers):
        if pointer.dest == node_to_rem:
            node_to_rem.pointers.pop(i)
            return pointer.path
        

def make_graph(n):
    nodes = [Node() for _ in range(n)]
    for i, node in enumerate(nodes):
        if (i * 2) % n == (i * 2 + 1) % n:
            node.pointers.append(Pointer(nodes[(i * 2) % n], '[01]'))
        else:
            node.pointers.append(Pointer(nodes[(i * 2) % n], '0'))
            node.pointers.append(Pointer(nodes[(i * 2 + 1) % n], '1'))
    return nodes
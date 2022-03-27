class Tree:
    def __init__(self, value, parent):
        self.parent = parent
        self.children = []
        self.value = value
        self.declared_vars = []     # 3 for PROGRAM types only

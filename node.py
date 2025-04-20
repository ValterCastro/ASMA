class Node:
    truck = None
    bin = None

    def __init__(self, name):
        self.name = name
        self.edge_list = set()

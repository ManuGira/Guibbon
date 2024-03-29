import tkinter as tk
from tkinter import ttk
from typing import Callable

CallbackTreeview = Callable[[], None]


class TreeviewWidget:
    def __init__(self, tk_frame, name, tree, on_click: CallbackTreeview):
        self.tk_frame = tk_frame
        self.name = name

        self.frame = tk.Frame(self.tk_frame)
        tk.Label(self.frame, text=self.name).pack(padx=2, side=tk.TOP, anchor=tk.W)
        self.tk_treeview = ttk.Treeview(self.frame)

        self.build_tree("", tree)
        self.tk_treeview.pack(padx=2, side=tk.TOP, anchor=tk.W)
        self.frame.pack(padx=2, side=tk.TOP, anchor=tk.W)

    def build_tree(self, parent, tree_node):
        assert isinstance(tree_node, TreeNode)
        for subtree_node in tree_node.children.values():
            tk_node = self.tk_treeview.insert(parent, tk.END, text=subtree_node.name)
            self.build_tree(tk_node, subtree_node)

class TreeNode:
    def __init__(self, name="", data=None):
        self.name = name
        self.data = data
        self.children = {}

    def set(self, path, data=None):
        if len(path) == 0:
            self.data = data
            return
        child_name = path[0]
        if child_name not in self.children.keys():
            self.children[child_name] = TreeNode(child_name)
        self.children[child_name].set(path[1:], data)

    def get(self, path):
        if len(path) == 0:
            return self
        child_name = path[0]
        return self.children[child_name].get(path[1:])

    def str(self, indent=0):
        lines = []
        data_str = "" if self.data is None else str(self.data)
        lines.append(f"{self.name}: {data_str}")
        print(self.name)
        for child in self.children.values():
            indent_str = "  : " * indent + "  + "
            lines.append(indent_str + child.str(indent+1))
        return "\n".join(lines)

    def __str__(self):
        return self.str()

    def depth_first_walk(self):
        print(self.name)
        yield [self.name], self.data, self
        for child in self.children.values():
            for subpath, subname, subchild in child.depth_first_walk():
                yield [self.name] + subpath, subname, subchild

def main():
    tree = TreeNode("master")
    tree.set(["mon", "petit", "node"], 12)
    tree.set(["mon", "petit", "node", "gentil"], 56)
    tree.set(["mon", "petit", "arbre"], [34])
    petit = tree.get(["mon", "petit", "arbre"])
    petit.data.append(3344)
    print(tree)

    for node in tree.depth_first_walk():
        print(node)

if __name__ == '__main__':
    main()
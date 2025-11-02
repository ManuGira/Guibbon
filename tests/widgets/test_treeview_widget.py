import unittest
import tkinter as tk
from unittest.mock import Mock

from guibbon.widgets.treeview_widget import TreeNode, TreeviewWidget


class TestTreeNode(unittest.TestCase):
    """Test suite for TreeNode class"""

    def test_create_empty_node(self) -> None:
        """Test creating an empty TreeNode"""
        node = TreeNode()
        self.assertEqual(node.name, "")
        self.assertIsNone(node.value)
        self.assertEqual(len(node.children), 0)

    def test_create_node_with_name(self) -> None:
        """Test creating a TreeNode with a name"""
        node = TreeNode("test_node")
        self.assertEqual(node.name, "test_node")
        self.assertIsNone(node.value)

    def test_create_node_with_value(self) -> None:
        """Test creating a TreeNode with a value"""
        node = TreeNode("test_node", 42)
        self.assertEqual(node.name, "test_node")
        self.assertEqual(node.value, 42)

    def test_set_value_on_root(self) -> None:
        """Test setting value on root node with empty path"""
        node = TreeNode("root")
        node.set([], 100)
        self.assertEqual(node.value, 100)

    def test_set_single_child(self) -> None:
        """Test setting a single child node"""
        root = TreeNode("root")
        root.set(["child"], "child_value")
        
        self.assertIn("child", root.children)
        self.assertEqual(root.children["child"].name, "child")
        self.assertEqual(root.children["child"].value, "child_value")

    def test_set_nested_children(self) -> None:
        """Test setting nested children"""
        root = TreeNode("root")
        root.set(["level1", "level2", "level3"], "deep_value")
        
        # Check level1
        self.assertIn("level1", root.children)
        level1 = root.children["level1"]
        
        # Check level2
        self.assertIn("level2", level1.children)
        level2 = level1.children["level2"]
        
        # Check level3
        self.assertIn("level3", level2.children)
        level3 = level2.children["level3"]
        self.assertEqual(level3.value, "deep_value")

    def test_set_multiple_children_same_parent(self) -> None:
        """Test setting multiple children under same parent"""
        root = TreeNode("root")
        root.set(["child1"], "value1")
        root.set(["child2"], "value2")
        
        self.assertEqual(len(root.children), 2)
        self.assertEqual(root.children["child1"].value, "value1")
        self.assertEqual(root.children["child2"].value, "value2")

    def test_set_overwrites_existing_value(self) -> None:
        """Test that setting overwrites existing value"""
        root = TreeNode("root")
        root.set(["child"], "original")
        root.set(["child"], "updated")
        
        self.assertEqual(root.children["child"].value, "updated")

    def test_get_root_node(self) -> None:
        """Test getting root node with empty path"""
        root = TreeNode("root", "root_value")
        result = root.get([])
        
        self.assertIs(result, root)
        self.assertEqual(result.value, "root_value")

    def test_get_direct_child(self) -> None:
        """Test getting direct child node"""
        root = TreeNode("root")
        root.set(["child"], "child_value")
        
        child = root.get(["child"])
        self.assertEqual(child.name, "child")
        self.assertEqual(child.value, "child_value")

    def test_get_nested_node(self) -> None:
        """Test getting nested node"""
        root = TreeNode("root")
        root.set(["a", "b", "c"], "nested_value")
        
        node_c = root.get(["a", "b", "c"])
        self.assertEqual(node_c.name, "c")
        self.assertEqual(node_c.value, "nested_value")

    def test_get_intermediate_node(self) -> None:
        """Test getting intermediate node in path"""
        root = TreeNode("root")
        root.set(["a", "b", "c"], "leaf_value")
        
        node_b = root.get(["a", "b"])
        self.assertEqual(node_b.name, "b")
        self.assertIsNone(node_b.value)
        self.assertIn("c", node_b.children)

    def test_str_representation(self) -> None:
        """Test string representation of tree"""
        root = TreeNode("root", "root_val")
        root.set(["child"], "child_val")
        
        result = str(root)
        
        self.assertIn("root:", result)
        self.assertIn("child:", result)

    def test_depth_first_walk_single_node(self) -> None:
        """Test depth-first walk on single node"""
        root = TreeNode("root", "value")
        
        nodes = list(root.depth_first_walk())
        
        self.assertEqual(len(nodes), 1)
        path, value, node = nodes[0]
        self.assertEqual(path, ["root"])
        self.assertEqual(value, "value")
        self.assertIs(node, root)

    def test_depth_first_walk_with_children(self) -> None:
        """Test depth-first walk with multiple children"""
        root = TreeNode("root")
        root.set(["child1"], "val1")
        root.set(["child2"], "val2")
        
        nodes = list(root.depth_first_walk())
        
        # Should have root + 2 children = 3 nodes
        self.assertEqual(len(nodes), 3)
        
        # First should be root
        self.assertEqual(nodes[0][0], ["root"])

    def test_depth_first_walk_nested(self) -> None:
        """Test depth-first walk with nested structure"""
        root = TreeNode("root")
        root.set(["a", "b"], "leaf")
        
        nodes = list(root.depth_first_walk())
        
        # Should have root, a, b = 3 nodes
        self.assertEqual(len(nodes), 3)
        paths = [node[0] for node in nodes]
        self.assertIn(["root"], paths)
        self.assertIn(["root", "a"], paths)
        self.assertIn(["root", "a", "b"], paths)


# Shared Tk root for all tests to avoid tkinter instability
_tk_root = None


def setUpModule():
    """Create a single shared Tk root for all tests in this module"""
    global _tk_root
    _tk_root = tk.Tk()
    _tk_root.withdraw()  # Hide the window


def tearDownModule():
    """Destroy the shared Tk root after all tests"""
    global _tk_root
    if _tk_root:
        try:
            _tk_root.destroy()
        except tk.TclError:
            pass
        _tk_root = None


class TestTreeviewWidget(unittest.TestCase):
    """Test suite for TreeviewWidget class"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        # Use a Frame as child of the shared root instead of creating new Tk()
        self.frame = tk.Frame(_tk_root, width=400, height=300)
        self.frame.pack(expand=True, fill='both')
        # Update to ensure frame is rendered and has dimensions
        _tk_root.update_idletasks()
        _tk_root.update()

    def tearDown(self) -> None:
        """Clean up after tests"""
        try:
            self.frame.destroy()
        except tk.TclError:
            pass

    def test_create_treeview_widget(self) -> None:
        """Test basic TreeviewWidget creation"""
        tree = TreeNode("root")
        tree.set(["child1"], "value1")
        
        callback = Mock()
        widget = TreeviewWidget(self.frame, "Test Tree", tree, callback)
        
        self.assertEqual(widget.name, "Test Tree")
        self.assertIs(widget.tree, tree)
        self.assertIs(widget.on_click, callback)
        self.assertIsNotNone(widget.tk_treeview)

    def test_treeview_widget_with_empty_tree(self) -> None:
        """Test TreeviewWidget with empty tree"""
        tree = TreeNode("root")
        callback = Mock()
        
        widget = TreeviewWidget(self.frame, "Empty Tree", tree, callback)
        
        self.assertIsNotNone(widget)
        self.assertEqual(len(tree.children), 0)

    def test_treeview_widget_with_nested_tree(self) -> None:
        """Test TreeviewWidget with nested tree structure"""
        tree = TreeNode("root")
        tree.set(["parent", "child", "grandchild"], "deep_value")
        
        callback = Mock()
        widget = TreeviewWidget(self.frame, "Nested Tree", tree, callback)
        
        self.assertIsNotNone(widget)
        # Verify tree structure is intact
        node = tree.get(["parent", "child", "grandchild"])
        self.assertEqual(node.value, "deep_value")

    def test_treeview_widget_with_multiple_branches(self) -> None:
        """Test TreeviewWidget with multiple branches"""
        tree = TreeNode("root")
        tree.set(["branch1", "leaf1"], "value1")
        tree.set(["branch2", "leaf2"], "value2")
        tree.set(["branch3"], "value3")
        
        callback = Mock()
        widget = TreeviewWidget(self.frame, "Multi-branch Tree", tree, callback)
        
        self.assertIsNotNone(widget)
        self.assertEqual(len(tree.children), 3)

    def test_build_tree_populates_treeview(self) -> None:
        """Test that build_tree populates the ttk.Treeview"""
        tree = TreeNode("root")
        tree.set(["child1"], "value1")
        tree.set(["child2"], "value2")
        
        callback = Mock()
        widget = TreeviewWidget(self.frame, "Test", tree, callback)
        
        # Get all items in treeview
        children = widget.tk_treeview.get_children()
        
        # Should have 2 top-level children
        self.assertEqual(len(children), 2)

    def test_callback_not_called_on_creation(self) -> None:
        """Test that callback is not called during widget creation"""
        tree = TreeNode("root")
        tree.set(["child"], "value")
        
        callback = Mock()
        TreeviewWidget(self.frame, "Test", tree, callback)
        
        callback.assert_not_called()

    def test_treeview_widget_with_complex_values(self) -> None:
        """Test TreeviewWidget with complex value types"""
        tree = TreeNode("root")
        tree.set(["list_node"], [1, 2, 3])
        tree.set(["dict_node"], {"key": "value"})
        tree.set(["int_node"], 42)
        
        callback = Mock()
        TreeviewWidget(self.frame, "Complex Tree", tree, callback)
        
        # Verify values are stored correctly
        self.assertEqual(tree.get(["list_node"]).value, [1, 2, 3])
        self.assertEqual(tree.get(["dict_node"]).value, {"key": "value"})
        self.assertEqual(tree.get(["int_node"]).value, 42)


if __name__ == "__main__":
    unittest.main()

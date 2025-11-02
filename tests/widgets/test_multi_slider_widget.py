import unittest
import tkinter as tk
import guibbon as gbn
from guibbon.widgets.multi_slider_widget import MultiSliderWidget, MultiSliderOverlay


class TestMultiSliderWidget(unittest.TestCase):
    def setUp(self):
        self.winname = "win0"
        gbn.namedWindow(self.winname)
        self.guibbon_instance = gbn.Guibbon.instances["win0"]
        self.callback_count = 0
        self.last_positions_values = None

    def tearDown(self):
        # Clean up
        if self.winname in gbn.Guibbon.instances:
            self.guibbon_instance.on_closing()

    def callback(self, positions_values):
        self.callback_count += 1
        self.last_positions_values = positions_values

    def test_create_multislider(self):
        """Test basic creation of multislider widget"""
        values = [0, 1, 2, 3, 4, 5]
        initial_positions = [1, 3]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test MultiSlider",
            values=values,
            initial_indexes=initial_positions,
            on_drag=self.callback,
            on_release=self.callback
        )
        
        self.assertIsNotNone(ms)
        self.assertIsInstance(ms, MultiSliderWidget)
        
        # Check initial positions
        positions = ms.get_positions()
        self.assertEqual(positions, initial_positions)
        
        # Check values
        result_values = ms.get_values()
        self.assertEqual(result_values, values)

    def test_get_positions(self):
        """Test getting cursor positions"""
        values = list(range(10))
        initial_positions = [2, 5, 8]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=values,
            initial_indexes=initial_positions
        )
        
        positions = ms.get_positions()
        self.assertEqual(positions, initial_positions)
        self.assertEqual(len(positions), 3)

    def test_set_positions_without_callback(self):
        """Test setting positions without triggering callback"""
        values = list(range(10))
        initial_positions = [1, 5]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=values,
            initial_indexes=initial_positions,
            on_drag=self.callback
        )
        
        self.callback_count = 0
        new_positions = [3, 7]
        ms.set_positions(new_positions, trigger_callback=False)
        
        # Callback should not be triggered
        self.assertEqual(self.callback_count, 0)
        
        # Positions should be updated
        positions = ms.get_positions()
        self.assertEqual(positions, new_positions)

    def test_set_positions_with_callback(self):
        """Test setting positions with callback trigger"""
        values = list(range(10))
        initial_positions = [1, 5]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=values,
            initial_indexes=initial_positions,
            on_drag=self.callback,
            on_release=self.callback
        )
        
        self.callback_count = 0
        new_positions = [2, 6]
        ms.set_positions(new_positions, trigger_callback=True)
        
        # Both on_drag and on_release callbacks should be triggered
        self.assertEqual(self.callback_count, 2)
        
        # Check the callback received correct data
        self.assertIsNotNone(self.last_positions_values)
        expected = [(2, values[2]), (6, values[6])]
        self.assertEqual(self.last_positions_values, expected)

    def test_get_values(self):
        """Test getting values list"""
        values = ['a', 'b', 'c', 'd', 'e']
        initial_positions = [0, 2]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=values,
            initial_indexes=initial_positions
        )
        
        result_values = ms.get_values()
        self.assertEqual(result_values, values)
        # Verify it's a copy, not the same list
        self.assertIsNot(result_values, values)

    def test_set_values_without_callback(self):
        """Test setting new values without triggering callback"""
        initial_values = list(range(5))
        initial_positions = [1, 3]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=initial_values,
            initial_indexes=initial_positions,
            on_drag=self.callback
        )
        
        self.callback_count = 0
        new_values = list(range(10, 20))
        ms.set_values(new_values, trigger_callback=False)
        
        # Callback should not be triggered
        self.assertEqual(self.callback_count, 0)
        
        # Values should be updated
        result_values = ms.get_values()
        self.assertEqual(result_values, new_values)

    def test_set_values_with_callback(self):
        """Test setting new values with callback trigger"""
        initial_values = list(range(5))
        initial_positions = [1, 3]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=initial_values,
            initial_indexes=initial_positions,
            on_drag=self.callback,
            on_release=self.callback
        )
        
        self.callback_count = 0
        new_values = list(range(10, 20))
        ms.set_values(new_values, trigger_callback=True)
        
        # Both callbacks should be triggered
        self.assertEqual(self.callback_count, 2)

    def test_add_cursor(self):
        """Test adding a cursor dynamically"""
        values = list(range(10))
        initial_positions = [2]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=values,
            initial_indexes=initial_positions
        )
        
        # Initially should have 1 cursor
        self.assertEqual(len(ms.get_positions()), 1)
        
        # Add a cursor at position 5
        ms.add_cursor(position=5)
        
        # Should now have 2 cursors
        positions = ms.get_positions()
        self.assertEqual(len(positions), 2)
        self.assertIn(5, positions)

    def test_remove_cursor(self):
        """Test removing a cursor"""
        values = list(range(10))
        initial_positions = [2, 5, 8]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=values,
            initial_indexes=initial_positions
        )
        
        # Initially should have 3 cursors
        self.assertEqual(len(ms.get_positions()), 3)
        
        # Remove a cursor
        ms.remove_cursor()
        
        # Should now have 2 cursors
        positions = ms.get_positions()
        self.assertEqual(len(positions), 2)

    def test_remove_cursor_minimum(self):
        """Test that at least one cursor remains"""
        values = list(range(10))
        initial_positions = [5]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=values,
            initial_indexes=initial_positions
        )
        
        # Try to remove the only cursor
        ms.remove_cursor()
        
        # Should still have 1 cursor (minimum)
        positions = ms.get_positions()
        self.assertEqual(len(positions), 1)

    def test_positions_adjust_when_values_shrink(self):
        """Test that positions are adjusted when value list shrinks"""
        initial_values = list(range(10))
        initial_positions = [3, 7, 9]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=initial_values,
            initial_indexes=initial_positions
        )
        
        # Set shorter value list
        new_values = list(range(5))
        ms.set_values(new_values, trigger_callback=False)
        
        # Positions beyond the new max should be clamped
        positions = ms.get_positions()
        for pos in positions:
            self.assertLessEqual(pos, len(new_values) - 1)

    def test_set_positions_adds_cursors(self):
        """Test that set_positions can add cursors if needed"""
        values = list(range(10))
        initial_positions = [2]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=values,
            initial_indexes=initial_positions
        )
        
        # Set more positions than current cursors
        new_positions = [1, 3, 5, 7]
        ms.set_positions(new_positions, trigger_callback=False)
        
        # Should now have 4 cursors
        positions = ms.get_positions()
        self.assertEqual(len(positions), 4)
        self.assertEqual(positions, new_positions)

    def test_set_positions_removes_cursors(self):
        """Test that set_positions can remove cursors if needed"""
        values = list(range(10))
        initial_positions = [1, 3, 5, 7]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=values,
            initial_indexes=initial_positions
        )
        
        # Set fewer positions than current cursors
        new_positions = [2, 6]
        ms.set_positions(new_positions, trigger_callback=False)
        
        # Should now have 2 cursors
        positions = ms.get_positions()
        self.assertEqual(len(positions), 2)
        self.assertEqual(positions, new_positions)

    def test_callback_parameters(self):
        """Test that callbacks receive correct parameters"""
        values = ['apple', 'banana', 'cherry', 'date']
        initial_positions = [0, 2]
        
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=values,
            initial_indexes=initial_positions,
            on_drag=self.callback
        )
        
        # Trigger callback by setting positions
        new_positions = [1, 3]
        ms.set_positions(new_positions, trigger_callback=True)
        
        # Check callback received correct format: list of (position, value) tuples
        expected = [(1, 'banana'), (3, 'date')]
        self.assertEqual(self.last_positions_values, expected)

    def test_none_callbacks(self):
        """Test that widget works with None callbacks"""
        values = list(range(5))
        initial_positions = [1, 3]
        
        # Should not raise exception
        ms = gbn.create_multislider(
            winname=self.winname,
            multislider_name="Test",
            values=values,
            initial_indexes=initial_positions,
            on_drag=None,
            on_release=None
        )
        
        # Operations should work without callbacks
        ms.set_positions([0, 4], trigger_callback=True)
        ms.add_cursor(2)
        ms.remove_cursor()
        
        # Should complete without errors
        self.assertEqual(len(ms.get_positions()), 2)


if __name__ == "__main__":
    unittest.main()

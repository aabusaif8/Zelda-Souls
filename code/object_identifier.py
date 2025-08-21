class ObjectIdentifier:
    def __init__(self):
        # Multi-tile object mapping (top-left, top-right, bottom-left, bottom-right) -> object index
        self.multi_tile_objects = {
            (0, 1, 8, 9): 1,
            (16, 17, 24, 25): 2,
            (2, 3, 10, 11): 3,
            (18, 19, 26, 27): 4,
            (34, 35, 42, 43): 5,
            (32, 33, 40, 41): 6,
            (20, 21, 28, 29): 7,
            (36, 37, 44, 45): 10,
            (64, 65, 72, 73): 17,
            (4, 5, 12, 13): 20,
            (6, 7, 14, 15): 15,
        }
        
        # Track processed positions to avoid duplicates
        self.processed_positions = set()
        
    def get_object_at_position(self, layout, row, col):
        """
        Check if there's a 2x2 object pattern starting at the given position.
        Returns (object_index, positions_to_mark) or (None, None) if no pattern found.
        """
        # Skip if this position was already processed or is empty
        if (row, col) in self.processed_positions or layout[row][col] == '-1':
            return None, None
            
        try:
            # Get the 2x2 tile pattern
            top_left = int(layout[row][col])
            top_right = int(layout[row][col + 1]) if col + 1 < len(layout[row]) and layout[row][col + 1] != '-1' else -1
            bottom_left = int(layout[row + 1][col]) if row + 1 < len(layout) and layout[row + 1][col] != '-1' else -1
            bottom_right = int(layout[row + 1][col + 1]) if (row + 1 < len(layout) and 
                                                            col + 1 < len(layout[row + 1]) and 
                                                            layout[row + 1][col + 1] != '-1') else -1
            
            pattern = (top_left, top_right, bottom_left, bottom_right)
            
            # Check if this pattern matches any known objects
            if pattern in self.multi_tile_objects:
                object_index = self.multi_tile_objects[pattern]
                
                # Return the object index and positions that should be marked as processed
                positions_to_mark = [
                    (row, col),
                    (row, col + 1),
                    (row + 1, col),
                    (row + 1, col + 1)
                ]
                
                return object_index, positions_to_mark
                
        except (IndexError, ValueError):
            # Handle edge cases where pattern extends beyond map boundaries
            pass
            
        return None, None
    
    def mark_positions_processed(self, positions):
        """Mark a list of positions as processed to avoid duplicates."""
        if positions:
            for pos in positions:
                self.processed_positions.add(pos)
    
    def reset(self):
        """Reset processed positions (call this when starting a new map)."""
        self.processed_positions.clear()
    
    def add_pattern(self, pattern, object_index):
        """Add a new 2x2 pattern mapping."""
        self.multi_tile_objects[pattern] = object_index
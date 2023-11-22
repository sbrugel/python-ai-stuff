class Tile:
    """
    Represents a tile in the maze
    """
    def __init__(self, obstacle: bool):
        self.obstacle = obstacle
        self.open = False
        self.closed = False

    def add_to_open(self):
        self.open = True

    def add_to_closed(self):
        self.closed = True
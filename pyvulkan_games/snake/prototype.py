class SnakePrototype:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.size = 20
        self.positions = [(width//2, height//2)]
        self.dir = (self.size, 0)
    def step(self):
        head_x, head_y = self.positions[0]
        dx, dy = self.dir
        new_x = (head_x + dx) % self.width
        new_y = (head_y + dy) % self.height
        self.positions.insert(0, (new_x, new_y))
        if len(self.positions) > 10:
            self.positions.pop()
    def set_dir(self, dx, dy):
        self.dir = (dx*self.size, dy*self.size)

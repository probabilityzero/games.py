class PongPrototype:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pw = 10
        self.ph = 80
        self.ball_size = 12
        self.left_y = height // 2 - self.ph // 2
        self.right_y = height // 2 - self.ph // 2
        self.ball_x = width // 2
        self.ball_y = height // 2
        self.ball_dx = 4
        self.ball_dy = 3
    def step(self):
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        if self.ball_y <= 0 or self.ball_y + self.ball_size >= self.height:
            self.ball_dy = -self.ball_dy
        if self.ball_x <= self.pw:
            if self.left_y <= self.ball_y <= self.left_y + self.ph:
                self.ball_dx = -self.ball_dx
            else:
                self.ball_x, self.ball_y = self.width//2, self.height//2
        if self.ball_x + self.ball_size >= self.width - self.pw:
            if self.right_y <= self.ball_y <= self.right_y + self.ph:
                self.ball_dx = -self.ball_dx
            else:
                self.ball_x, self.ball_y = self.width//2, self.height//2
    def move_left(self, dy):
        self.left_y = max(0, min(self.height - self.ph, self.left_y + dy))
    def move_right(self, dy):
        self.right_y = max(0, min(self.height - self.ph, self.right_y + dy))
    def get_drawables(self):
        rects = []
        rects.append((0, self.left_y, self.pw, self.ph, (0.9, 0.1, 0.1)))
        rects.append((self.width - self.pw, self.right_y, self.pw, self.ph, (0.1, 0.1, 0.9)))
        rects.append((self.ball_x, self.ball_y, self.ball_size, self.ball_size, (0.95, 0.95, 0.2)))
        return rects

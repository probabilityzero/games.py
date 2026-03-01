import glfw
import time
import random
from ..graphics.opengl_fallback import OpenGLRenderer

CELL = 20

class SnakeGame:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.renderer = OpenGLRenderer(width, height, title="Snake 3D Shader")
        self.running = False
        self.grid_w = width // CELL
        self.grid_h = height // CELL
        self.positions = [(self.grid_w//2, self.grid_h//2)]
        self.dir = (1, 0)
        self.next_dir = self.dir
        self.grow = 3
        self.food = None
        self.last_tick = time.time()
        self.tick_rate = 0.10
        self.start_time = time.time()

        # camera/navigation
        self.unit = 1.0
        # place camera above and behind the grid so cubes are visible by default
        cam_y = max(4.0, (self.grid_h * self.unit) * 0.6)
        cam_z = (self.grid_h * self.unit) * 1.0 + 4.0
        self.cam = {
            'pos': (0.0, cam_y, cam_z),
            'yaw': 0.0,
            'pitch': -35.0,
            'fov': 60.0,
        }
        self.mouse_last = (0.0, 0.0)
        self.rotating = False
        self.cam_speed = 6.0

    def place_food(self):
        while True:
            x = random.randint(1, self.grid_w-2)
            y = random.randint(1, self.grid_h-2)
            if (x,y) not in self.positions:
                self.food = (x,y)
                return

    def start(self):
        self.renderer.init_window()
        self.renderer.window_hints = None
        window = self.renderer.window
        # capture initial mouse
        self.mouse_last = glfw.get_cursor_pos(window)
        self.running = True
        self.place_food()
        print('Controls: Arrow keys = snake, Mouse drag = rotate camera, WASD = move camera, Q/E = up/down, H = toggle shader')

        while self.running and not glfw.window_should_close(window):
            now = time.time()
            # input: snake uses arrow keys, camera uses WASD/QE
            if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
                if self.dir != (0,1):
                    self.next_dir = (0,1)
            if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
                if self.dir != (0,-1):
                    self.next_dir = (0,-1)
            if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
                if self.dir != (1,0):
                    self.next_dir = (-1,0)
            if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
                if self.dir != (-1,0):
                    self.next_dir = (1,0)

            # Camera navigation
            now_mouse = glfw.get_cursor_pos(window)
            mx, my = now_mouse
            lm_x, lm_y = self.mouse_last
            left_pressed = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS
            if left_pressed:
                dx = mx - lm_x
                dy = my - lm_y
                self.cam['yaw'] += dx * 0.15
                self.cam['pitch'] -= dy * 0.12
                self.cam['pitch'] = max(-89.0, min(89.0, self.cam['pitch']))
            self.mouse_last = (mx, my)

            # keyboard camera movement (WASD = forward/left/back/right, Q/E up/down)
            import math
            yaw_rad = math.radians(self.cam['yaw'])
            pitch_rad = math.radians(self.cam['pitch'])
            forward = (math.cos(pitch_rad) * math.sin(yaw_rad), math.sin(pitch_rad), math.cos(pitch_rad) * math.cos(yaw_rad))
            right = (math.sin(yaw_rad - math.pi/2.0), 0.0, math.cos(yaw_rad - math.pi/2.0))
            speed = self.cam_speed * max(0.001, (now - self.last_tick if now - self.last_tick>0 else 0.016))
            cx, cy, cz = self.cam['pos']
            if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
                cx += forward[0] * speed
                cy += forward[1] * speed
                cz += forward[2] * speed
            if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
                cx -= forward[0] * speed
                cy -= forward[1] * speed
                cz -= forward[2] * speed
            if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
                cx += right[0] * speed
                cz += right[2] * speed
            if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
                cx -= right[0] * speed
                cz -= right[2] * speed
            if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
                cy += speed
            if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
                cy -= speed
            self.cam['pos'] = (cx, cy, cz)

            # toggle shader
            if glfw.get_key(window, glfw.KEY_H) == glfw.PRESS:
                # simple debounce by sleeping a bit
                self._shader_on = getattr(self, '_shader_on', True)
                self._shader_on = not self._shader_on
                time.sleep(0.15)

            # tick
            if now - self.last_tick >= self.tick_rate:
                self.last_tick = now
                self.dir = self.next_dir
                hx, hy = self.positions[0]
                dx, dy = self.dir
                nx = (hx + dx) % self.grid_w
                ny = (hy + dy) % self.grid_h
                new_head = (nx, ny)
                if new_head in self.positions:
                    # collision -> reset
                    self.positions = [(self.grid_w//2, self.grid_h//2)]
                    self.dir = (1,0)
                    self.next_dir = self.dir
                    self.grow = 3
                    self.place_food()
                else:
                    self.positions.insert(0, new_head)
                    if self.food and new_head == self.food:
                        self.grow += 3
                        self.place_food()
                    if self.grow > 0:
                        self.grow -= 1
                    else:
                        self.positions.pop()

            # render shader background
            t = time.time() - self.start_time
            mx, my = glfw.get_cursor_pos(window)
            # flip mouse Y to shader convention
            mouse = (mx, self.height - my, 0.0, 0.0)
            # draw shader background optionally
            try:
                shader_path = __import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'shaders', 'truchet.frag')
                shader_path = __import__('os').path.normpath(shader_path)
                if getattr(self, '_shader_on', True):
                    self.renderer.draw_shader_from_files(shader_path, time_sec=t, mouse=mouse)
                else:
                    # clear to a dark color
                    from OpenGL import GL as gl
                    gl.glClearColor(0.03, 0.03, 0.05, 1.0)
                    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            except Exception:
                # if shader fails, clear to dark and continue
                from OpenGL import GL as gl
                gl.glClearColor(0.03, 0.03, 0.05, 1.0)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

            # build 3D cube list from grid positions (centered around origin, X-Z plane)
            cubes = []
            offset_x = (self.grid_w / 2.0) * self.unit
            offset_z = (self.grid_h / 2.0) * self.unit
            for i, (x, y) in enumerate(self.positions):
                wx = (x * self.unit) - offset_x
                wz = (y * self.unit) - offset_z
                wy = self.unit * 0.5
                # color head brighter
                if i == 0:
                    col = (0.2, 1.0, 0.3)
                else:
                    col = (0.05, 0.6, 0.25)
                cubes.append((wx, wy, wz, col))
            if self.food:
                fx, fy = self.food
                wx = (fx * self.unit) - offset_x
                wz = (fy * self.unit) - offset_z
                wy = self.unit * 0.5
                cubes.append((wx, wy, wz, (1.0, 0.2, 0.2)))

            # draw 3D scene
            try:
                self.renderer.draw_3d_cubes(cubes, unit=self.unit, camera=self.cam)
            except Exception:
                # fall back to orthographic overlay if 3D fails
                rects = []
                for x, y in self.positions:
                    px = x * CELL
                    py = y * CELL
                    rects.append((px, py, CELL, CELL, (0.1, 0.9, 0.2)))
                if self.food:
                    fx, fy = self.food
                    rects.append((fx*CELL, fy*CELL, CELL, CELL, (0.9, 0.2, 0.2)))
                self.renderer.draw_rects(rects)

            glfw.poll_events()
            self.renderer.present()
            time.sleep(0.001)

        self.renderer.cleanup()


if __name__ == '__main__':
    g = SnakeGame(800, 600)
    g.start()

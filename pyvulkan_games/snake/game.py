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
        self.unit = 1.0
        # continuous 3D head position (centered at grid center)
        self.head_pos = (0.0, 0.0, 0.0)
        self.head_forward = (0.0, 0.0, -1.0)
        self.speed = 6.0
        self.segment_spacing = 0.5
        # segments list of vec3 positions (head first)
        self.segments = [(0.0, 0.0, 0.0)]
        self.grow = 10
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
        # aim camera at the scene origin so cubes are in front
        self.cam['target'] = (0.0, 0.0, 0.0)
        self.mouse_last = (0.0, 0.0)
        self.rotating = False
        self.cam_speed = 6.0

    def place_food(self):
        while True:
            gx = random.randint(1, self.grid_w-2)
            gz = random.randint(1, self.grid_h-2)
            # convert to world coords centered
            wx = (gx - self.grid_w/2.0) * self.unit
            wz = (gz - self.grid_h/2.0) * self.unit
            pos = (wx, 0.0, wz)
            if pos not in self.segments:
                self.food = pos
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
            # input: continuous movement controls
            # left/right rotate, up/down forward/back
            import math
            yaw_speed = 90.0
            if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
                ang = math.radians(-yaw_speed * max(0.001, now - self.last_tick))
                cx, cy, cz = self.head_forward
                sx = cx * math.cos(ang) - cz * math.sin(ang)
                sz = cx * math.sin(ang) + cz * math.cos(ang)
                self.head_forward = (sx, cy, sz)
            if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
                ang = math.radians(yaw_speed * max(0.001, now - self.last_tick))
                cx, cy, cz = self.head_forward
                sx = cx * math.cos(ang) - cz * math.sin(ang)
                sz = cx * math.sin(ang) + cz * math.cos(ang)
                self.head_forward = (sx, cy, sz)
            # forward/back
            acc = 0.0
            if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
                acc += 1.0
            if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
                acc -= 1.0
            # update speed
            self.speed += acc * 8.0 * max(0.001, now - self.last_tick)
            self.speed = max(1.0, min(20.0, self.speed))

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

                # mouse-right steering: if right button pressed, use mouse dx to yaw head
                right_pressed = glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS
                if right_pressed:
                    mx2, my2 = glfw.get_cursor_pos(window)
                    dx = mx2 - self.mouse_last[0]
                    ang = dx * 0.0025
                    import math
                    cx, cy, cz = self.head_forward
                    sx = cx * math.cos(ang) - cz * math.sin(ang)
                    sz = cx * math.sin(ang) + cz * math.cos(ang)
                    self.head_forward = (sx, cy, sz)

            # integrate head movement continuous
            dt = max(0.0, now - self.last_tick)
            hx, hy, hz = self.head_pos
            fx, fy, fz = self.head_forward
            # normalize forward
            import math
            fl = math.sqrt(fx*fx + fy*fy + fz*fz)
            if fl == 0: fl = 1.0
            fx, fy, fz = fx/fl, fy/fl, fz/fl
            nx = hx + fx * self.speed * dt
            ny = hy + fy * self.speed * dt
            nz = hz + fz * self.speed * dt
            self.head_pos = (nx, ny, nz)

            # append segment if far enough
            lx, ly, lz = self.segments[0]
            dist = math.sqrt((nx-lx)**2 + (ny-ly)**2 + (nz-lz)**2)
            if dist >= self.segment_spacing:
                self.segments.insert(0, (nx, ny, nz))
                if self.grow > 0:
                    self.grow -= 1
                else:
                    # trim to max segments
                    maxlen = 128
                    if len(self.segments) > maxlen:
                        self.segments = self.segments[:maxlen]

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

            # prepare uniforms for first/third-person shader rendering
            try:
                shader_path = __import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'shaders', 'truchet_snake_fp.frag')
                shader_path = __import__('os').path.normpath(shader_path)

                # snake segments are world-space vec3 positions
                sp = []
                for s in self.segments:
                    sp.append((float(s[0]), float(s[1]), float(s[2])))

                # food is vec3
                if self.food:
                    food_v = (float(self.food[0]), float(self.food[1]), float(self.food[2]))
                else:
                    food_v = (0.0, -10.0, 0.0)

                # camera third-person behind head
                hx, hy, hz = self.head_pos
                fx, fy, fz = self.head_forward
                # normalize forward
                import math
                fl = math.sqrt(fx*fx + fy*fy + fz*fz)
                if fl == 0: fl = 1.0
                fxn, fyn, fzn = fx/fl, fy/fl, fz/fl
                cam_dist = 3.0
                cam_height = 1.2
                cam_pos = (hx - fxn*cam_dist, hy + cam_height, hz - fzn*cam_dist)
                cam_dir = (fxn, fyn, fzn)

                self.renderer._extra_uniforms = {
                    'uSnakeLen': int(len(sp)),
                    'uSnake': sp,
                    'uFood': food_v,
                    'uStartPos': (0.0, 0.0, 0.0),
                    'uBackgroundColor': (0.03, 0.08, 0.12),
                    'iCameraPos': cam_pos,
                    'iCameraDir': cam_dir,
                }

                self.renderer.draw_shader_from_files(shader_path, time_sec=t, mouse=mouse)

                # HUD lines
                head = self.segments[0] if len(self.segments)>0 else (0.0,0.0,0.0)
                dist_food = 0.0
                if self.food:
                    import math
                    dx = head[0]-self.food[0]
                    dy = head[1]-self.food[1]
                    dz = head[2]-self.food[2]
                    dist_food = math.sqrt(dx*dx+dy*dy+dz*dz)
                lines = [
                    f"Shader: {'ON' if getattr(self,'_shader_on',True) else 'OFF'}",
                    f"Segments: {len(self.segments)}",
                    f"Head: {head[0]:.2f}, {head[1]:.2f}, {head[2]:.2f}",
                    f"Food dist: {dist_food:.2f}",
                    f"Speed: {self.speed:.2f}",
                ]
                try:
                    self.renderer.draw_hud(lines)
                except Exception:
                    pass
            except Exception:
                from OpenGL import GL as gl
                gl.glClearColor(0.03, 0.03, 0.05, 1.0)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

            glfw.poll_events()
            self.renderer.present()
            time.sleep(0.001)

        self.renderer.cleanup()


if __name__ == '__main__':
    g = SnakeGame(800, 600)
    g.start()

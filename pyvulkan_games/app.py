import time
import os
import glfw
from .graphics import VulkanRenderer, OpenGLRenderer
from .snake import SnakePrototype
try:
    import GPUtil
except Exception:
    GPUtil = None

class App:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.renderer = None
        self.last_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.snake = None
    def choose_backend(self):
        vk = VulkanRenderer()
        vk.init_vulkan()
        if vk.vk_available and os.environ.get("VULKAN_SDK"):
            try:
                vk.init_window()
                self.renderer = vk
                return
            except Exception:
                try:
                    vk.cleanup()
                except Exception:
                    pass
        ogl = OpenGLRenderer(self.width, self.height)
        ogl.init_window()
        self.renderer = ogl

    def _on_key(self, window, key, scancode, action, mods):
        if action not in (glfw.PRESS, glfw.REPEAT):
            return
        if key in (glfw.KEY_RIGHT, glfw.KEY_D):
            self.snake.set_dir(1, 0)
        elif key in (glfw.KEY_LEFT, glfw.KEY_A):
            self.snake.set_dir(-1, 0)
        elif key in (glfw.KEY_UP, glfw.KEY_W):
            self.snake.set_dir(0, 1)
        elif key in (glfw.KEY_DOWN, glfw.KEY_S):
            self.snake.set_dir(0, -1)
    def run(self):
        self.choose_backend()
        self.snake = SnakePrototype(self.width, self.height)
        glfw.set_key_callback(self.renderer.window, self._on_key)
        step_interval = 0.1
        last_step = time.time()
        while not glfw.window_should_close(self.renderer.window):
            start = time.time()
            glfw.poll_events()
            self.frame_count += 1
            now = time.time()
            if now - self.last_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_time = now
            gpu_info = "Unavailable"
            if GPUtil:
                try:
                    gpus = GPUtil.getGPUs()
                    gpu_info = gpus[0].name if gpus else "Unknown"
                except Exception:
                    gpu_info = "Unknown"
            if gpu_info in ("Unavailable", "Unknown"):
                try:
                    from OpenGL import GL as gl
                    renderer_str = gl.glGetString(gl.GL_RENDERER)
                    if renderer_str:
                        gpu_info = renderer_str.decode('utf-8')
                except Exception:
                    pass
            print(f"FPS:{self.fps} GPU:{gpu_info}", end="\r")
            now = time.time()
            if now - last_step >= step_interval:
                self.snake.step()
                last_step = now
            try:
                self.renderer.draw_snake(self.snake.positions, size=self.snake.size)
            except Exception:
                pass
            self.renderer.present()
            elapsed = time.time() - start
            if elapsed < 0.001:
                time.sleep(0.001 - elapsed)
        self.renderer.cleanup()

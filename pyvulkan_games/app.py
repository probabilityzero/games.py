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
    def run(self):
        self.choose_backend()
        self.snake = SnakePrototype(self.width, self.height)
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
            keys = glfw.get_key(self.renderer.window, glfw.KEY_RIGHT), glfw.get_key(self.renderer.window, glfw.KEY_LEFT), glfw.get_key(self.renderer.window, glfw.KEY_UP), glfw.get_key(self.renderer.window, glfw.KEY_DOWN)
            if keys[0] == glfw.PRESS:
                self.snake.set_dir(1, 0)
            if keys[1] == glfw.PRESS:
                self.snake.set_dir(-1, 0)
            if keys[2] == glfw.PRESS:
                self.snake.set_dir(0, 1)
            if keys[3] == glfw.PRESS:
                self.snake.set_dir(0, -1)
            self.snake.step()
            try:
                self.renderer.draw_snake(self.snake.positions, size=self.snake.size)
            except Exception:
                pass
            self.renderer.present()
            elapsed = time.time() - start
            if elapsed < 0.001:
                time.sleep(0.001 - elapsed)
        self.renderer.cleanup()

import glfw
import time
from OpenGL import GL as gl

class OpenGLRenderer:
    def __init__(self, width=1280, height=720, title="PV Games (OpenGL)"):
        self.width = width
        self.height = height
        self.title = title
        self.window = None
    def init_window(self):
        if not glfw.init():
            raise RuntimeError("glfw.init failed")
        glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("create_window failed")
        glfw.make_context_current(self.window)
        gl.glViewport(0, 0, self.width, self.height)
        gl.glClearColor(0.05, 0.05, 0.07, 1.0)
    def draw_snake(self, positions, size=20):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, self.width, 0, self.height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glColor3f(0.2, 0.3, 0.25)
        cx = self.width // 2
        cy = self.height // 2
        half = 40
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(cx - half, cy - half)
        gl.glVertex2f(cx + half, cy - half)
        gl.glVertex2f(cx + half, cy + half)
        gl.glVertex2f(cx - half, cy + half)
        gl.glEnd()
        gl.glColor3f(0.1, 0.9, 0.2)
        for x, y in positions:
            gl.glBegin(gl.GL_QUADS)
            gl.glVertex2f(x, y)
            gl.glVertex2f(x + size, y)
            gl.glVertex2f(x + size, y + size)
            gl.glVertex2f(x, y + size)
            gl.glEnd()
    def present(self):
        if self.window:
            glfw.swap_buffers(self.window)
    def cleanup(self):
        if self.window:
            glfw.destroy_window(self.window)
            glfw.terminate()

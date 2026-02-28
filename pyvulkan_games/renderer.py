try:
    import vulkan as vk
    VULKAN_AVAILABLE = True
except Exception:
    VULKAN_AVAILABLE = False
import glfw
import time

class VulkanRenderer:
    def __init__(self, width=1280, height=720, title="PV Games"):
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        self.vk_available = VULKAN_AVAILABLE
        self.instance = None
    def init_window(self):
        if not glfw.init():
            raise RuntimeError("glfw.init failed")
        glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("create_window failed")
    def init_vulkan(self):
        if not self.vk_available:
            return
        try:
            import vulkan as vk
            self.vk = vk
        except Exception:
            self.vk_available = False
    def present(self):
        if self.window:
            glfw.swap_buffers(self.window)
    def cleanup(self):
        if self.window:
            glfw.destroy_window(self.window)
            glfw.terminate()

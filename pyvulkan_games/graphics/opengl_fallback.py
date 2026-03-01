import glfw
import time
from OpenGL import GL as gl
from OpenGL import GLU as glu
import os


_shader_cache = {}

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

    def _compile_shader(self, vert_src, frag_src):
        key = (vert_src, frag_src)
        if key in _shader_cache:
            return _shader_cache[key]

        def compile(src, sh_type):
            sh = gl.glCreateShader(sh_type)
            gl.glShaderSource(sh, src)
            gl.glCompileShader(sh)
            ok = gl.glGetShaderiv(sh, gl.GL_COMPILE_STATUS)
            if not ok:
                info = gl.glGetShaderInfoLog(sh).decode('utf-8')
                raise RuntimeError('Shader compile error: ' + info)
            return sh

        vs = compile(vert_src, gl.GL_VERTEX_SHADER)
        fs = compile(frag_src, gl.GL_FRAGMENT_SHADER)
        prog = gl.glCreateProgram()
        gl.glAttachShader(prog, vs)
        gl.glAttachShader(prog, fs)
        gl.glLinkProgram(prog)
        ok = gl.glGetProgramiv(prog, gl.GL_LINK_STATUS)
        if not ok:
            info = gl.glGetProgramInfoLog(prog).decode('utf-8')
            raise RuntimeError('Program link error: ' + info)

        _shader_cache[key] = prog
        return prog

    def draw_shader_from_files(self, frag_path, time_sec=0.0, mouse=(0,0,0,0)):
        if not os.path.exists(frag_path):
            raise FileNotFoundError(frag_path)
        with open(frag_path, 'r', encoding='utf-8') as f:
            frag_src = f.read()

        vert_src = """
#version 120
void main(){ gl_Position = gl_Vertex; }
"""

        prog = self._compile_shader(vert_src, frag_src)
        gl.glUseProgram(prog)

        loc = gl.glGetUniformLocation(prog, 'iResolution')
        if loc != -1:
            gl.glUniform2f(loc, float(self.width), float(self.height))
        loc = gl.glGetUniformLocation(prog, 'iTime')
        if loc != -1:
            gl.glUniform1f(loc, float(time_sec))
        loc = gl.glGetUniformLocation(prog, 'iMouse')
        if loc != -1:
            x, y, b1, b2 = mouse
            gl.glUniform4f(loc, float(x), float(y), float(b1), float(b2))

        extra_uniforms = getattr(self, '_extra_uniforms', None)
        if extra_uniforms:
            for name, val in extra_uniforms.items():
                loc = gl.glGetUniformLocation(prog, name)
                if loc == -1:
                    continue
                if isinstance(val, float):
                    gl.glUniform1f(loc, val)
                elif isinstance(val, int):
                    gl.glUniform1i(loc, val)
                elif isinstance(val, tuple) or isinstance(val, list):
                    ln = len(val)
                    if ln == 2 and all(isinstance(x, (float, int)) for x in val):
                        gl.glUniform2f(loc, float(val[0]), float(val[1]))
                    elif ln == 3:
                        gl.glUniform3f(loc, float(val[0]), float(val[1]), float(val[2]))
                    elif ln == 4:
                        gl.glUniform4f(loc, float(val[0]), float(val[1]), float(val[2]), float(val[3]))
                    else:
                        # vec2 array
                        if all(isinstance(x, (tuple, list)) and len(x) == 2 for x in val):
                            flat = []
                            for v in val:
                                flat.extend([float(v[0]), float(v[1])])
                            try:
                                from OpenGL.arrays import vbo
                                import numpy as _np
                                arr = _np.array(flat, dtype=_np.float32)
                                gl.glUniform2fv(loc, int(len(flat)//2), arr)
                            except Exception:
                                try:
                                    for idx, v in enumerate(val):
                                        loci = gl.glGetUniformLocation(prog, f"{name}[{idx}]")
                                        if loci != -1:
                                            gl.glUniform2f(loci, float(v[0]), float(v[1]))
                                except Exception:
                                    pass
                        # vec3 array
                        elif all(isinstance(x, (tuple, list)) and len(x) == 3 for x in val):
                            flat = []
                            for v in val:
                                flat.extend([float(v[0]), float(v[1]), float(v[2])])
                            try:
                                import numpy as _np
                                arr = _np.array(flat, dtype=_np.float32)
                                gl.glUniform3fv(loc, int(len(flat)//3), arr)
                            except Exception:
                                try:
                                    for idx, v in enumerate(val):
                                        loci = gl.glGetUniformLocation(prog, f"{name}[{idx}]")
                                        if loci != -1:
                                            gl.glUniform3f(loci, float(v[0]), float(v[1]), float(v[2]))
                                except Exception:
                                    pass

        gl.glViewport(0, 0, int(self.width), int(self.height))
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        gl.glBegin(gl.GL_QUADS)
        gl.glVertex3f(-1.0, -1.0, 0.0)
        gl.glVertex3f(1.0, -1.0, 0.0)
        gl.glVertex3f(1.0, 1.0, 0.0)
        gl.glVertex3f(-1.0, 1.0, 0.0)
        gl.glEnd()

        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)

        gl.glUseProgram(0)
        if hasattr(self, '_extra_uniforms'):
            delattr(self, '_extra_uniforms')

    def draw_3d_cubes(self, cube_positions, unit=1.0, camera=None):
        # camera: dict with pos (x,y,z), yaw (deg), pitch (deg), fov
        if camera is None:
            camera = {'pos': (0, 5, 10), 'yaw': 0.0, 'pitch': -30.0, 'fov': 60.0}

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        # set perspective
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        aspect = float(self.width) / float(self.height) if self.height != 0 else 1.0
        glu.gluPerspective(camera.get('fov', 60.0), aspect, 0.1, 100.0)

        # set camera
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        cx, cy, cz = camera.get('pos', (0,5,10))
        # if a target is provided, look at it; otherwise compute from yaw/pitch
        if 'target' in camera:
            tx, ty, tz = camera['target']
            glu.gluLookAt(cx, cy, cz, tx, ty, tz, 0.0, 1.0, 0.0)
        else:
            yaw = camera.get('yaw', 0.0)
            pitch = camera.get('pitch', 0.0)
            import math
            cyaw = math.radians(yaw)
            cp = math.radians(pitch)
            fx = math.cos(cp) * math.sin(cyaw)
            fy = math.sin(cp)
            fz = math.cos(cp) * math.cos(cyaw)
            lx = cx + fx
            ly = cy + fy
            lz = cz + fz
            glu.gluLookAt(cx, cy, cz, lx, ly, lz, 0.0, 1.0, 0.0)

        # simple directional light as color tint
        gl.glColor3f(0.2, 0.9, 0.2)

        # draw cubes
        half = unit * 0.5
        def draw_unit_cube(size):
            s = size * 0.5
            # 6 faces
            gl.glBegin(gl.GL_QUADS)
            # front
            gl.glNormal3f(0,0,1)
            gl.glVertex3f(-s, -s, s)
            gl.glVertex3f(s, -s, s)
            gl.glVertex3f(s, s, s)
            gl.glVertex3f(-s, s, s)
            # back
            gl.glNormal3f(0,0,-1)
            gl.glVertex3f(s, -s, -s)
            gl.glVertex3f(-s, -s, -s)
            gl.glVertex3f(-s, s, -s)
            gl.glVertex3f(s, s, -s)
            # left
            gl.glNormal3f(-1,0,0)
            gl.glVertex3f(-s, -s, -s)
            gl.glVertex3f(-s, -s, s)
            gl.glVertex3f(-s, s, s)
            gl.glVertex3f(-s, s, -s)
            # right
            gl.glNormal3f(1,0,0)
            gl.glVertex3f(s, -s, s)
            gl.glVertex3f(s, -s, -s)
            gl.glVertex3f(s, s, -s)
            gl.glVertex3f(s, s, s)
            # top
            gl.glNormal3f(0,1,0)
            gl.glVertex3f(-s, s, s)
            gl.glVertex3f(s, s, s)
            gl.glVertex3f(s, s, -s)
            gl.glVertex3f(-s, s, -s)
            # bottom
            gl.glNormal3f(0,-1,0)
            gl.glVertex3f(-s, -s, -s)
            gl.glVertex3f(s, -s, -s)
            gl.glVertex3f(s, -s, s)
            gl.glVertex3f(-s, -s, s)
            gl.glEnd()

        for px, py, pz, col in cube_positions:
            r, g, b = col
            gl.glColor3f(r, g, b)
            gl.glPushMatrix()
            gl.glTranslatef(px, py, pz)
            draw_unit_cube(unit)
            gl.glPopMatrix()

        # restore matrices
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)

        gl.glDisable(gl.GL_DEPTH_TEST)

    def _try_init_glut(self):
        try:
            from OpenGL import GLUT as glut
        except Exception:
            return None

        if getattr(self, '_glut_inited', False):
            return glut

        try:
            # initialize GLUT once for bitmap font use
            glut.glutInit()
        except Exception:
            try:
                import sys
                glut.glutInit(sys.argv)
            except Exception:
                return None

        self._glut_inited = True
        return glut

    def draw_text(self, x, y, text, size=18, color=(1.0,1.0,1.0)):
        glut = self._try_init_glut()
        if not glut:
            return False
        from OpenGL import GL as gl
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(0, self.width, 0, self.height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glDisable(gl.GL_DEPTH_TEST)
        r,g,b = color
        gl.glColor3f(r,g,b)
        gl.glRasterPos2f(x, y)
        for ch in text:
            try:
                glut.glutBitmapCharacter(glut.GLUT_BITMAP_HELVETICA_18, ord(ch))
            except Exception:
                pass
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        return True

    def draw_hud(self, lines):
        # draw translucent background and text lines (top-left)
        from OpenGL import GL as gl
        # orthographic overlay
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPushMatrix()
        gl.glLoadIdentity()
        gl.glOrtho(0, self.width, 0, self.height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glPushMatrix()
        gl.glLoadIdentity()

        # background box
        pad = 8
        line_h = 20
        w = 300
        h = line_h * len(lines) + pad*2
        x = 8
        y = self.height - h - 8
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glColor4f(0.03, 0.03, 0.05, 0.7)
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f(x, y)
        gl.glVertex2f(x + w, y)
        gl.glVertex2f(x + w, y + h)
        gl.glVertex2f(x, y + h)
        gl.glEnd()
        gl.glDisable(gl.GL_BLEND)

        # draw lines of text using GLUT if available, else set window title as fallback
        drawn = False
        try:
            glut = self._try_init_glut()
            if glut:
                for i, line in enumerate(lines):
                    self.draw_text(x + pad, y + h - pad - (i+1)*line_h + 4, line)
                drawn = True
        except Exception:
            drawn = False

        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glPopMatrix()
        gl.glMatrixMode(gl.GL_MODELVIEW)

        if not drawn and hasattr(self, 'window') and self.window:
            try:
                title = ' | '.join(lines[:3])
                glfw.set_window_title(self.window, title)
            except Exception:
                pass

    def draw_rects(self, rects):
        for x, y, w, h, col in rects:
            r, g, b = col
            gl.glColor3f(r, g, b)
            gl.glBegin(gl.GL_QUADS)
            gl.glVertex2f(x, y)
            gl.glVertex2f(x + w, y)
            gl.glVertex2f(x + w, y + h)
            gl.glVertex2f(x, y + h)
            gl.glEnd()
    def present(self):
        if self.window:
            glfw.swap_buffers(self.window)
    def cleanup(self):
        if self.window:
            glfw.destroy_window(self.window)
            glfw.terminate()

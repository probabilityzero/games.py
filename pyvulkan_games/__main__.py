from .app import App

def main():
    print("PV Games Launcher")
    print("1) Snake")
    print("2) Pong")
    print("q) Quit")
    choice = input("Choose game: ")
    if choice.strip() == '1':
        App().run()
    elif choice.strip() == '2':
        from .graphics import OpenGLRenderer
        from .pong.prototype import PongPrototype
        from .snake.prototype import SnakePrototype
        render = OpenGLRenderer(800, 600)
        render.init_window()
        pong = PongPrototype(800, 600)
        import glfw, time
        glfw.set_key_callback(render.window, lambda w,k,sc,a,m: None)
        last = time.time()
        while not glfw.window_should_close(render.window):
            start = time.time()
            glfw.poll_events()
            if glfw.get_key(render.window, glfw.KEY_W) == glfw.PRESS:
                pong.move_left(-8)
            if glfw.get_key(render.window, glfw.KEY_S) == glfw.PRESS:
                pong.move_left(8)
            if glfw.get_key(render.window, glfw.KEY_UP) == glfw.PRESS:
                pong.move_right(-8)
            if glfw.get_key(render.window, glfw.KEY_DOWN) == glfw.PRESS:
                pong.move_right(8)
            if time.time() - last > 0.016:
                pong.step()
                last = time.time()
            render.draw_rects(pong.get_drawables())
            render.present()
        render.cleanup()

if __name__ == '__main__':
    main()

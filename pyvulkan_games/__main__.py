from .app import App

def _run_pong():
    from .graphics import OpenGLRenderer
    from .pong.prototype import PongPrototype
    import glfw, time
    render = OpenGLRenderer(800, 600)
    render.init_window()
    pong = PongPrototype(800, 600)
    last = time.time()
    while not glfw.window_should_close(render.window):
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

def main():
    try:
        import dearpygui.dearpygui as dpg
    except Exception:
        print("PV Games Launcher")
        print("1) Snake")
        print("2) Pong")
        print("q) Quit")
        choice = input("Choose game: ")
        if choice.strip() == '1':
            App().run()
        elif choice.strip() == '2':
            _run_pong()
        return
    dpg.create_context()
    dpg.create_viewport(title='PV Games Launcher', width=400, height=200)
    selected = {'choice': None}
    def _on_snake():
        selected['choice'] = 'snake'
        dpg.stop_dearpygui()
    def _on_pong():
        selected['choice'] = 'pong'
        dpg.stop_dearpygui()
    def _on_quit():
        selected['choice'] = None
        dpg.stop_dearpygui()
    with dpg.window(label='Launcher', width=400, height=200):
        dpg.add_text('PV Games')
        dpg.add_button(label='Play Snake', callback=lambda s,_=None: _on_snake())
        dpg.add_button(label='Play Pong', callback=lambda s,_=None: _on_pong())
        dpg.add_button(label='Quit', callback=lambda s,_=None: _on_quit())
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
    if selected['choice'] == 'snake':
        App().run()
    elif selected['choice'] == 'pong':
        _run_pong()

if __name__ == '__main__':
    main()

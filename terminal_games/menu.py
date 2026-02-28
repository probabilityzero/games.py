import curses
from terminal_games.constants import SNAKE_ART, DEFAULT_CONFIG

# --- Utility functions (no changes) ---
def safe_addstr(stdscr, y, x, text, color=None):
    height, width = stdscr.getmaxyx()
    if 0 <= y < height and 0 <= x < width:
        try:
            if color:
                stdscr.addstr(y, x, text, color)
            else:
                stdscr.addstr(y, x, text)
        except curses.error:
            pass

def get_color(config, element):
    theme = config["theme"]
    color_data = config["colors"].get(theme, config["colors"]["Default"])
    if element in color_data:
        color_index = list(color_data.keys()).index(element) + 1
        return curses.color_pair(color_index)
    else:
        return curses.COLOR_WHITE | curses.COLOR_BLACK

def get_input(stdscr, y, x, prompt, color):
    safe_addstr(stdscr, y, x, prompt, color)
    curses.echo()
    try:
        input_str = stdscr.getstr(y, x + len(prompt), 5).decode('utf-8')
    except UnicodeDecodeError:
        input_str = ""
    curses.noecho()
    return input_str

# --- draw_menu_box (with box dimension calculations) ---
def draw_menu_box(stdscr, top_y, height, width, title, config):
    margin_sides = 5
    margin_bottom = 2

    # Calculate box width (maximum 48, minimum depends on screen)
    box_width = min(width - 2 * margin_sides, 64)
    box_width = max(box_width, len(title) + 4)  # Ensure title fits

    # Calculate box height (48 / golden ratio, shrinks with screen)
    box_height = min(height - top_y - margin_bottom - 1, 16)
    box_height = max(box_height, 5)  # Ensure minimum height

    start_y = top_y
    start_x = (width - box_width) // 2  # Center the box horizontally
    color = get_color(config, "border")
    safe_addstr(stdscr, start_y, start_x, "┌" + "─" * (box_width - 2) + "┐", color)
    title_x = start_x + (box_width - len(title)) // 2
    safe_addstr(stdscr, start_y, title_x, title, get_color(config, "menu") | curses.A_BOLD)
    for y in range(start_y + 1, start_y + box_height):
        safe_addstr(stdscr, y, start_x, "│", color)
        safe_addstr(stdscr, y, start_x + box_width - 1, "│", color)
    safe_addstr(stdscr, start_y + box_height, start_x, "└" + "─" * (box_width - 2) + "┘", color)
    return start_y + 1, start_x + 1, box_height - 1, box_width - 2

# --- show_options_menu (Wrap-Around Navigation) ---
def show_options_menu(stdscr, config, init_colors_main, save_config_main):
    height, width = stdscr.getmaxyx()
    menu_items = {
        "New Game": "",
        "Speed": "",
        "Sound": "",
        "Theme": "",
        "Help": "",
        "Exit": ""
    }
    menu_keys = list(menu_items.keys())
    current_row = 0
    scroll_offset = 0

    while True:
        stdscr.clear()
        # --- Positioning the art, like in main.py ---
        art_start_y = height // 2 - len(SNAKE_ART) // 2 - 6  # Calculate art position
        for i, line in enumerate(SNAKE_ART):
            safe_addstr(stdscr, art_start_y + i, (width - len(line)) // 2, line, get_color(config, "menu"))
        # ---------------------------------------------

        box_top_y = art_start_y + len(SNAKE_ART) + 2  # Position box below art
        title = "OPTIONS"
        start_y, start_x, box_height, box_width = draw_menu_box(stdscr, box_top_y, height, width, title, config)

        item_y = start_y + 1
        item_height = 2
        visible_items = box_height // item_height

        shortcut_col_width = 1
        name_col_width = 12
        status_col_width = 10

        shortcut_col_x = start_x
        name_col_x = shortcut_col_x + shortcut_col_width + 1
        status_col_x = start_x + box_width // 2  # Corrected status column x-coordinate

        for i in range(visible_items):
            index = i + scroll_offset
            if 0 <= index < len(menu_keys):
                key = menu_keys[index]
                shortcut = menu_items[key]
                y = item_y + i * item_height

                if key == "Sound":
                    status_text = "Enabled" if config['sound_enabled'] else "Disabled"
                elif key == "Speed":
                    status_text = str(config['level'])
                elif key == "Theme":
                    status_text = config['theme']
                else:
                    status_text = ""

                if index == current_row:
                    for x in range(start_x, start_x + box_width):
                        safe_addstr(stdscr, y, x, " ", get_color(config, "highlight"))
                    safe_addstr(stdscr, y, shortcut_col_x, shortcut, get_color(config, "highlight"))
                    safe_addstr(stdscr, y, name_col_x, key[:name_col_width], get_color(config, "highlight"))
                    safe_addstr(stdscr, y, status_col_x, status_text[:status_col_width], get_color(config, "highlight"))
                else:
                    safe_addstr(stdscr, y, shortcut_col_x, shortcut, get_color(config, "menu"))
                    safe_addstr(stdscr, y, name_col_x, key[:name_col_width], get_color(config, "menu"))
                    # Change color of status text to white
                    safe_addstr(stdscr, y, status_col_x, status_text[:status_col_width], curses.COLOR_WHITE)

        esc_back = "ESC Back"
        safe_addstr(stdscr, start_y + box_height + 1, start_x, esc_back, get_color(config, "menu"))
        stdscr.refresh()
        key = stdscr.getch()

        # --- Wrap-Around Navigation ---
        if key == curses.KEY_UP or key == ord('w'):
            current_row -= 1
            if current_row < 0:
                current_row = len(menu_keys) - 1  # Wrap to bottom
                scroll_offset = max(0, len(menu_keys) - visible_items) # Scroll
        elif key == curses.KEY_DOWN or key == ord('s'):
            current_row += 1
            if current_row >= len(menu_keys):
                current_row = 0  # Wrap to top
                scroll_offset = 0

        elif key == curses.KEY_MOUSE:
            _, _, _, _, bstate = curses.getmouse()
            if bstate & curses.WHEEL_UP:
                scroll_offset = max(0, scroll_offset - 1)
                current_row = max(0, current_row - 1)
            elif bstate & curses.WHEEL_DOWN:
                scroll_offset = min(scroll_offset + 1, max(0, len(menu_keys) - visible_items))
                current_row = min(len(menu_keys) - 1, current_row + 1)

        # Scrolling Logic
        if current_row >= scroll_offset + visible_items:
            scroll_offset = current_row - visible_items + 1
        if current_row < scroll_offset:
            scroll_offset = current_row

        # --- Hotkeys and Actions (no other changes) ---
        if key == ord('n'):
            return "new_game"
        elif key == ord('h'):
            show_help_screen(stdscr, config)
        elif key == ord('t'):
            config["theme"] = change_theme(stdscr, config)
            init_colors_main(config)
            current_row = 3
        elif key == ord('d'):
            config["sound_enabled"] = not config["sound_enabled"]
            current_row = 2
        elif key == 27 or key in (ord("f"), ord("o"), ord("m")):
            break
        elif key == ord('q'):
            return "quit"
        elif key == ord('p'):
            return "back"

        if current_row == 1 or 49 <= key <= 56:
            if key == curses.KEY_LEFT or key == ord('a'):
                config["level"] = max(1, config["level"] - 1)
            elif key == curses.KEY_RIGHT or key == ord('d'):
                config["level"] = min(8, config["level"] + 1)
            elif 49 <= key <= 56:
                config["level"] = key - 48
            current_row = 1

        elif key in (curses.KEY_ENTER, 10, 13):
            selected_option = menu_keys[current_row]
            if selected_option == "New Game":  return "new_game"
            if selected_option == "Help":      show_help_screen(stdscr, config)
            if selected_option == "Exit":      return "quit"

    save_config_main(config)
    return "back"

# --- Help Screen (Wrap-Around Navigation)---
HELP_TEXT = [
    "Controls:",
    "  - Arrow keys/WASD: Move",
    "  - M/O: Open Menu",
    "  - Q: Quit",
    "  - F/ESC: Pause/Play",
    "",
    "Gameplay:",
    "  - Eat food (*) to grow.",
    "  - Wrap around screen edges.",
    "  - Every 5th eat: bonus.",
    "",
    "Menu:",
    "  - New Game N: Start.",
    "  - Speed S: Difficulty.",
    "  - Sound D: On/off.",
    "  - Theme T: Change look.",
    "  - Help H: This screen.",
    "  - Exit Q: Quit.",
    "  - Back ESC/F: Return.",
    "",
]

def show_help_screen(stdscr, config):
    height, width = stdscr.getmaxyx()
    stdscr.clear()
    # --- Positioning the art, like in main.py ---
    art_start_y = height // 2 - len(SNAKE_ART) // 2 - 6
    for i, line in enumerate(SNAKE_ART):
        safe_addstr(stdscr, art_start_y + i, (width - len(line)) // 2, line, get_color(config, "menu"))
    # ---------------------------------------------

    box_top_y = art_start_y + len(SNAKE_ART) + 2   # Position box below art
    start_y, start_x, box_height, box_width = draw_menu_box(stdscr, box_top_y, height, width, "HELP", config)
    esc_back = "ESC Back"
    safe_addstr(stdscr, start_y + box_height + 1, start_x, esc_back, get_color(config, "menu"))
    available_lines = box_height - 1  # Adjust for the border
    scroll_offset = 0
    #current_row = 0  # Not needed for scrolling behavior

    while True:
        stdscr.clear()
        # --- Positioning the art (AGAIN, inside loop) ---
        art_start_y = height // 2 - len(SNAKE_ART) // 2 - 6
        for i, line in enumerate(SNAKE_ART):
            safe_addstr(stdscr, art_start_y + i, (width - len(line)) // 2, line, get_color(config, "menu"))
        # ---------------------------------------------
        box_top_y = art_start_y + len(SNAKE_ART) + 2
        start_y, start_x, box_height, box_width = draw_menu_box(stdscr, box_top_y, height, width, "HELP", config)
        safe_addstr(stdscr, start_y + box_height + 1, start_x, esc_back, get_color(config, "menu"))

        for i, line in enumerate(HELP_TEXT):
            line_y = start_y + 1 + i - scroll_offset
            if start_y < line_y < start_y + box_height:  # Corrected condition
                safe_addstr(stdscr, line_y, start_x + 2, line, get_color(config, "text"))

        stdscr.refresh()
        key = stdscr.getch()

        # --- Standard Scrolling in Help ---
        if key == curses.KEY_UP or key == ord('w'):
            scroll_offset = max(0, scroll_offset - 1)  # Only decrement, stop at 0

        elif key == curses.KEY_DOWN or key == ord('s'):
            # Calculate the maximum scroll offset *before* incrementing
            max_scroll = max(0, len(HELP_TEXT) - available_lines)
            scroll_offset = min(max_scroll, scroll_offset + 1) # Only increment, stop at max

        elif key == curses.KEY_MOUSE:
            _, _, _, _, bstate = curses.getmouse()
            if bstate & curses.WHEEL_UP:
                scroll_offset = max(0, scroll_offset - 1)
            elif bstate & curses.WHEEL_DOWN:
                max_scroll = max(0, len(HELP_TEXT) - available_lines)
                scroll_offset = min(max_scroll, scroll_offset + 1)

        elif key == ord('q'):
            return "quit"
        elif key == ord('p') or key == 27:
            break
        elif key != -1: # any other
            break

# --- change_theme (no changes) ---
def change_theme(stdscr, config):
    height, width = stdscr.getmaxyx()
    themes = list(config["colors"].keys())
    current_theme_index = themes.index(config["theme"])

    while True:
        stdscr.clear()
        message = "Select Theme: " + themes[current_theme_index]
        safe_addstr(stdscr, height // 2, (width - len(message)) // 2, message, get_color(config, "menu"))

        for i, theme in enumerate(themes):
            x = width // 2 - 10 + i * 10
            y = height // 2 + 2
            if i == current_theme_index:
                safe_addstr(stdscr, y, x, theme, get_color(config, "highlight"))
            else:
                safe_addstr(stdscr, y, x, theme, get_color(config, "menu"))

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_LEFT or key == ord('a'):
            current_theme_index = (current_theme_index - 1) % len(themes)
        elif key == curses.KEY_RIGHT or key == ord('d'):
            current_theme_index = (current_theme_index + 1) % len(themes)
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            return themes[current_theme_index]
        elif key == 27:
            return config["theme"]

# --- customize_colors (no changes) ---
def customize_colors(stdscr, config, init_colors_main):
    height, width = stdscr.getmaxyx()
    elements = list(config["custom_colors"].keys())
    current_element_index = 0
    current_color_index = 0  # 0:fg, 1:bg
    current_rgb_index = 0   # 0:Red, 1:Green, 2:Blue

    if not curses.can_change_color():
        stdscr.clear()
        message = "Your terminal does not support changing colors."
        safe_addstr(stdscr, height // 2, (width - len(message)) // 2, message)
        safe_addstr(stdscr, height // 2 + 2, (width - len("Press any key to return")) // 2, "Press any key to return")
        stdscr.refresh()
        stdscr.getch()
        return

    while True:
        stdscr.clear()
        title = "Customize Colors (RGB)"
        safe_addstr(stdscr, height // 2 - len(elements) // 2 - 6, (width - len(title)) // 2, title, curses.A_BOLD)

        for i, element in enumerate(elements):
            x = width // 3
            y = height // 2 - len(elements) // 2 + i
            fg, bg = config["custom_colors"][element]
            if i == current_element_index:
                safe_addstr(stdscr, y, x - 5, ">", get_color(config, "highlight"))
            safe_addstr(stdscr, y, x, f"{element}: ", get_color(config, "text"))
            safe_addstr(stdscr, y, x + 15, "  ", curses.color_pair(i + 1))
            safe_addstr(stdscr, y, x + 20, f"FG: {fg}, BG: {bg}", get_color(config, "text"))

        key = stdscr.getch()
        if key == curses.KEY_UP or key == ord('w'):
            current_element_index = (current_element_index - 1) % len(elements)
            current_color_index = 0
            current_rgb_index = 0
        elif key == curses.KEY_DOWN or key == ord('s'):
            current_element_index = (current_element_index + 1) % len(elements)
            current_color_index = 0
            current_rgb_index = 0
        elif key == curses.KEY_LEFT or key == ord('a'):
            current_rgb_index = (current_rgb_index - 1) % 3
        elif key == curses.KEY_RIGHT or key == ord('d'):
            current_rgb_index = (current_rgb_index + 1) % 3
        elif key == ord('\t'):
            current_color_index = (current_color_index + 1) % 2
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            fg, bg = config["custom_colors"][elements[current_element_index]]
            color_to_modify = fg if current_color_index == 0 else bg

            if isinstance(color_to_modify, tuple):
                color_list = list(color_to_modify)
                new_value_str = get_input(stdscr, height - 3, width // 2, f"Enter new value for {['R', 'G', 'B'][current_rgb_index]} (0-255): ", get_color(config, "text"))
                try:
                    new_value = int(new_value_str)
                    if 0 <= new_value <= 255:
                        color_list[current_rgb_index] = new_value
                        if current_color_index == 0:
                            config["custom_colors"][elements[current_element_index]] = (tuple(color_list), bg)
                        else:
                            config["custom_colors"][elements[current_element_index]] = (fg, tuple(color_list))
                except ValueError:
                    pass

        elif key == ord('q') or key == ord('Q'):
            config["theme"] = "custom"
            init_colors_main(config)
            return
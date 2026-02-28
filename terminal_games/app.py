# main.py
import curses
import random
import time
import json
import os
import winsound  # For Windows sound
from terminal_games.constants import SNAKE_SEGMENTS, DEFAULT_CONFIG, CONFIG_FILE, SNAKE_ART, FOOD_CHAR, BONUS_FOOD_CHAR, HORIZONTAL_BORDER_CHAR, VERTICAL_BORDER_CHAR
from terminal_games.menu import show_options_menu, show_help_screen  # For menu interactions

# --- Utility Functions (within main.py) ---
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

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                for key, default_value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = default_value
                    if isinstance(default_value, dict):
                        for sub_key, sub_default_value in default_value.items():
                            if sub_key not in config[key]:
                                config[key][sub_key] = sub_default_value
                return config
        except json.JSONDecodeError:
            print("Error: Invalid config file.  Using default settings.")
            return DEFAULT_CONFIG
    else:
        return DEFAULT_CONFIG


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def init_colors(config):
    curses.start_color()
    theme = config["theme"]
    color_data = config["colors"].get(theme, config["colors"]["Default"])
    for name, (fg, bg) in color_data.items():
        curses.init_pair(list(color_data.keys()).index(name) + 1, fg, bg)

def get_color(config, element):
    theme = config["theme"]
    color_data = config["colors"].get(theme, config["colors"]["Default"])
    if element not in color_data:
        return curses.COLOR_WHITE | curses.COLOR_BLACK
    color_index = list(color_data.keys()).index(element) + 1
    return curses.color_pair(color_index)
# --- End of Utility Functions ---

def display_game_ui(stdscr, score, config, width, paused):
    score_str = f"{score:04}"
    safe_addstr(stdscr, curses.LINES - 1, 1, score_str, get_color(config, "score"))
    menu_str = "M Menu"
    menu_x = width - len(menu_str) - 2
    safe_addstr(stdscr, curses.LINES - 1, menu_x, menu_str, get_color(config, "option"))

def draw_bonus_timer(stdscr, remaining_time, total_time, config, width):
    timer_width = width - 4
    filled_width = int(timer_width * (remaining_time / total_time))
    empty_width = timer_width - filled_width
    timer_y = curses.LINES - 2  # Adjusted position
    timer_str = "█" * filled_width + "░" * empty_width  # Use ░█ and ░
    safe_addstr(stdscr, timer_y, 2, timer_str, get_color(config, "bonus_timer"))

def get_snake_segment(prev_segment, current_segment, next_segment):
    px, py = prev_segment
    cx, cy = current_segment
    nx, ny = next_segment

    if px == cx == nx: return SNAKE_SEGMENTS["vertical"]    # Vertical
    if py == cy == ny: return SNAKE_SEGMENTS["horizontal"]  # Horizontal

    # Corners (curvy)
    if (cx > px and cy < ny) or (cx < nx and cy > py): return SNAKE_SEGMENTS["bottom_left"]
    if (cx > px and cy > ny) or (cx < nx and cy < py): return SNAKE_SEGMENTS["top_left"]
    if (cx < px and cy < ny) or (cx > nx and cy > py):  return SNAKE_SEGMENTS["bottom_right"]
    if (cx < px and cy > ny) or (cx > nx and cy < py): return SNAKE_SEGMENTS["top_right"]

    return "O"  # Fallback

def get_snake_head(direction):
      # More distinct head shapes
    if direction == curses.KEY_UP:    return "Λ"
    elif direction == curses.KEY_DOWN:  return "V"
    elif direction == curses.KEY_LEFT:  return "<"
    elif direction == curses.KEY_RIGHT: return ">"
    return "O"

def get_snake_tail(tail, second_last):
    tx, ty = tail
    sx, sy = second_last
    # Pointed tail
    if ty < sy:   return SNAKE_SEGMENTS["tail_left"]
    elif ty > sy: return SNAKE_SEGMENTS["tail_right"]
    elif tx < sx: return SNAKE_SEGMENTS["tail_up"]
    elif tx > sx: return SNAKE_SEGMENTS["tail_down"]
    return "o"

def create_food(snake, height, width, config, bonus_active=False):
    while True:
        food = [random.randint(0, height - 3), random.randint(0, width - 1)]
        if food not in snake:
            return food

def draw(stdscr, snake, food, bonus_food, bonus_active, score, config, paused, bonus_duration, bonus_start_time, direction, new_head):
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    for i, segment in enumerate(snake):
        if i == 0:
            segment_char = get_snake_head(direction)
        elif i == len(snake) - 1:
            segment_char = get_snake_tail(snake[-1], snake[-2])
        else:
            prev_segment = snake[i - 1]
            next_segment = snake[i + 1]
            segment_char = get_snake_segment(prev_segment, segment, next_segment)
        safe_addstr(stdscr, segment[0], segment[1], segment_char, get_color(config, "snake"))

    if bonus_active and bonus_food:
        safe_addstr(stdscr, bonus_food[0], bonus_food[1], BONUS_FOOD_CHAR, get_color(config, "bonus_food"))
    if not bonus_active or (bonus_active and new_head != food):
        safe_addstr(stdscr, food[0], food[1], FOOD_CHAR, get_color(config, "food"))

    # --- Single-line border ABOVE the score/status line ---
    border_y = height - 2
    for x in range(width):
        safe_addstr(stdscr, border_y, x, HORIZONTAL_BORDER_CHAR, get_color(config, "border"))

    safe_addstr(stdscr, height - 1, 0, " " * width, get_color(config, 'score'))
    display_game_ui(stdscr, score, config, width, paused)

    # --- Bonus Timer BELOW border ---
    if bonus_active:
        remaining_time = bonus_duration - (time.time() - bonus_start_time)
        draw_bonus_timer(stdscr, remaining_time, bonus_duration, config, width)

    if paused:
        pause_message = "PAUSED"
        safe_addstr(stdscr, height // 2, (width - len(pause_message)) // 2, pause_message, get_color(config, "menu") | curses.A_BOLD)

    stdscr.refresh()

def game_over_screen(stdscr, score):
    height, width = stdscr.getmaxyx()
    message1 = "Game Over!"
    message2 = f"Your Score: {score:04}"
    message3 = "Press any key to restart, or Q to quit"
    stdscr.clear()
    safe_addstr(stdscr, height // 2 - 2, (width - len(message1)) // 2, message1, curses.A_BOLD)
    safe_addstr(stdscr, height // 2 - 1, (width - len(message2)) // 2, message2)
    safe_addstr(stdscr, height // 2, (width - len(message3)) // 2, message3)
    stdscr.refresh()
    while True:
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            return False
        else:
            return True
def welcome_screen(stdscr, config):
    height, width = stdscr.getmaxyx()
    stdscr.clear()

    # Display Snake ASCII Art
    art_start_y = height // 2 - len(SNAKE_ART) // 2 - 6
    for i, line in enumerate(SNAKE_ART):
        safe_addstr(stdscr, art_start_y + i, (width - len(line)) // 2, line, get_color(config, "menu"))

    # Menu options
    resume_option = "Resume"  # Placeholder
    new_game_option = "New Game"
    menu_option = "Menu"  # Added Menu option
    exit_option = "Exit"  # Added Exit option

    # Calculate positions
    resume_y = art_start_y + len(SNAKE_ART) + 2
    new_game_y = resume_y + 2
    resume_x = (width - len(resume_option)) // 2
    new_game_x = (width - len(new_game_option)) // 2
    menu_y = new_game_y + 2       # Position Menu below New Game
    exit_y = menu_y + 2          # Position Exit below Menu

    # Display options with highlighting
    options = [resume_option, new_game_option, menu_option, exit_option]  # All options
    current_row = 0

    while True:
        for i, option in enumerate(options):
            x = (width - len(option)) // 2   # Calculate x position,  removed extra +2 for the padding.
            y = resume_y + i * 2  # Calculate y based on index

            if i == current_row:
                # Add padding spaces around highlighted option *ONLY* when it's the current row.
                safe_addstr(stdscr, y, x, option, get_color(config, "highlight"))
            else:
                safe_addstr(stdscr, y, x, option, get_color(config, "menu"))

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP or key == ord('w') or key == ord('W'):
            current_row = (current_row - 1) % len(options)  # Wrap around
        elif key == curses.KEY_DOWN or key == ord('s') or key == ord('S'):
            current_row = (current_row + 1) % len(options)  # Wrap around
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            if current_row == 0: return "resume"  # Resume
            if current_row == 1: return "new_game" # New Game
            if current_row == 2: return "menu"    # Menu
            if current_row == 3: return "quit"    # Exit
        elif key == ord(' ') or key == ord('p'):
            return "resume"
        elif key == ord('n') or key == ord('N'):
            return "new_game"
        elif key == ord('o') or key == ord('m'):
            return "menu"
        elif key == ord('q') or key == ord('Q'):
            return "quit"

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    config = load_config()
    init_colors(config)

    # --- Welcome Screen ---
    choice = welcome_screen(stdscr, config)
    if choice == -1:  # Quit
        return
    elif choice == 0:  # Resume Saved Game (Placeholder)
        # In a real game, you would load game state here.
        pass
    # --- End Welcome Screen ---
    height, width = stdscr.getmaxyx()
    snake = [[height // 2, width // 2], [height // 2, width // 2 -1]] # start with head and tail
    direction = curses.KEY_RIGHT
    food = create_food(snake, height, width, config)
    score = 0
    level_speeds = [150, 150, 120, 120, 100, 100, 80, 80]  # Consistent speed
    eat_count = 0
    bonus_active = False
    bonus_food = None
    bonus_start_time = 0
    bonus_duration = 0
    paused = False
    new_head = [height // 2, width // 2] # Initialize
    stdscr.timeout(level_speeds[config["level"] -1]) # Setting up a constent speed.

    while True:
        key = stdscr.getch()
        if key == curses.KEY_RESIZE:
            curses.resizeterm(*stdscr.getmaxyx())
            height, width = stdscr.getmaxyx()
            draw(stdscr, snake, food, bonus_food, bonus_active, score, config, paused, bonus_duration, bonus_start_time, direction, new_head)
            continue

        # --- Pause/Resume (F, ESC) ---
        if key == ord('p') or key == ord('P') or key == ord(' ') or key == 27:
            paused = not paused

        # --- Menu (M, O) - Works even when paused ---
        if key == ord('m') or key == ord('M') or key == ord('o') or key == ord('O'):
                option_result = show_options_menu(stdscr, config, init_colors, save_config)
                if option_result == "new_game":
                    snake = [[height // 2, width // 2],[height//2, width//2 -1]]; direction = curses.KEY_RIGHT; food = create_food(snake, height, width, config); score = 0;  eat_count = 0; bonus_active = False; bonus_food = None; paused = True
                    stdscr.timeout(level_speeds[config["level"] - 1]) # Consistent speed.
                    draw(stdscr, snake, food, bonus_food, bonus_active, score, config, paused, bonus_duration, bonus_start_time, direction, new_head)
                    continue
                elif option_result == "quit":
                    break
                draw(stdscr, snake, food, bonus_food, bonus_active, score, config, paused, bonus_duration, bonus_start_time, direction, new_head)
                continue
        # --- Quit (Q) ---
        if key == ord('q') or key == ord('Q'):  # Allow quitting anytime
            break

        # --- Help Screen (H) ---
        if key == ord('h') or key == ord('H'):
            show_help_screen(stdscr, config)
            draw(stdscr, snake, food, bonus_food, bonus_active, score, config, paused, bonus_duration, bonus_start_time, direction, new_head)
            continue

        # --- Game Logic (only if not paused) ---
        if not paused:
            # --- Movement ---
            if key == curses.KEY_UP or key in (ord('w'), ord('W')):
                if direction != curses.KEY_DOWN: direction = curses.KEY_UP
            elif key == curses.KEY_DOWN or key in (ord('s'), ord('S')):
                if direction != curses.KEY_UP: direction = curses.KEY_DOWN
            elif key == curses.KEY_LEFT or key in (ord('a'), ord('A')):
                if direction != curses.KEY_RIGHT: direction = curses.KEY_LEFT
            elif key == curses.KEY_RIGHT or key in (ord('d'), ord('D')):
                if direction != curses.KEY_LEFT: direction = curses.KEY_RIGHT

            new_head = [snake[0][0], snake[0][1]]
            if      direction == curses.KEY_UP:    new_head[0] -= 1
            elif direction == curses.KEY_DOWN:  new_head[0] += 1
            elif direction == curses.KEY_LEFT:  new_head[1] -= 1
            elif direction == curses.KEY_RIGHT: new_head[1] += 1

            new_head[0] = new_head[0] % (height - 2)
            new_head[1] = new_head[1] % width

            # --- Game Over: Self-Collision ---
            if new_head in snake:
                if game_over_screen(stdscr, score):
                    snake = [[height // 2, width // 2],[height//2, width//2 -1]]; direction = curses.KEY_RIGHT; food = create_food(snake, height, width, config); score = 0;  eat_count = 0; bonus_active = False; bonus_food = None; paused = False
                    stdscr.timeout(level_speeds[config["level"] - 1])
                    draw(stdscr, snake, food, bonus_food, bonus_active, score, config, paused, bonus_duration, bonus_start_time, direction, new_head)
                    continue
                else:
                    break # Quit

            snake.insert(0, new_head)

            if bonus_active:
                if new_head == bonus_food:
                    time_taken = time.time() - bonus_start_time
                    bonus_multiplier = max(0, int((bonus_duration - time_taken) * config["level"]))
                    score += 10 * bonus_multiplier
                    bonus_active = False
                    bonus_food = None
                    food = create_food(snake, height, width, config)
                    try:  # --- Sound: Bonus ---
                        winsound.PlaySound("bonus.wav", winsound.SND_ASYNC)
                    except:
                        pass
                elif time.time() - bonus_start_time > bonus_duration:
                    bonus_active = False
                    bonus_food = None
                    food = create_food(snake, height, width, config)

            if new_head == food:
                score += config["level"]
                eat_count += 1
                if eat_count % 5 == 0:
                    bonus_active = True
                    bonus_food = create_food(snake, height, width, config, bonus_active=True)
                    bonus_start_time = time.time()
                    bonus_duration = width * 0.15 * (9 - config["level"])
                    food = create_food(snake, height, width, config)
                else:
                    food = create_food(snake, height, width, config)
                try:  # --- Sound: Eat ---
                    winsound.PlaySound("eat.wav", winsound.SND_ASYNC)
                except:
                    pass
            else:
                if not bonus_active:
                    snake.pop()

        draw(stdscr, snake, food, bonus_food, bonus_active, score, config, paused, bonus_duration, bonus_start_time, direction, new_head)

if __name__ == "__main__":
    curses.wrapper(main)
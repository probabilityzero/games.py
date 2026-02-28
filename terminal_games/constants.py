# constants.py
import curses

CONFIG_FILE = "snake_config.json"

DEFAULT_CONFIG = {
    "level": 1,
    "theme": "Default",
    "snake_char": "O",  # Fallback character
    "food_char": "*",
    "wall_char": "#",
    "empty_char": " ",
    "sound_enabled": True,  # Add sound setting
    "colors": {
        "Default": {
            "snake": (curses.COLOR_GREEN, curses.COLOR_BLACK),
            "food": (curses.COLOR_RED, curses.COLOR_BLACK),
            "wall": (curses.COLOR_WHITE, curses.COLOR_BLACK),
            "text": (curses.COLOR_WHITE, curses.COLOR_BLACK),
            "menu": (curses.COLOR_CYAN, curses.COLOR_BLACK),
            "highlight": (curses.COLOR_BLACK, curses.COLOR_CYAN),
            "quit": (curses.COLOR_RED, curses.COLOR_BLACK),
            "option": (curses.COLOR_YELLOW, curses.COLOR_BLACK),
            "score": (curses.COLOR_WHITE, curses.COLOR_BLACK),
            "bonus_timer": (curses.COLOR_BLUE, curses.COLOR_BLACK),
            "bonus_food": (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
            "border": (curses.COLOR_WHITE, curses.COLOR_BLACK),
        },
        "dark": {  # Make sure all themes have all elements
           "snake": (curses.COLOR_GREEN, curses.COLOR_BLACK),
            "food": (curses.COLOR_RED, curses.COLOR_BLACK),
            "wall": (curses.COLOR_WHITE, curses.COLOR_BLACK),
            "text": (curses.COLOR_WHITE, curses.COLOR_BLACK),
            "menu": (curses.COLOR_CYAN, curses.COLOR_BLACK),
            "highlight": (curses.COLOR_BLACK, curses.COLOR_CYAN),
            "quit": (curses.COLOR_RED, curses.COLOR_BLACK),
            "option": (curses.COLOR_YELLOW, curses.COLOR_BLACK),
            "score": (curses.COLOR_WHITE, curses.COLOR_BLACK),
            "bonus_timer": (curses.COLOR_BLUE, curses.COLOR_BLACK),
            "bonus_food": (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
            "border": (curses.COLOR_WHITE, curses.COLOR_BLACK),
        },
        "light": {
            "snake": (curses.COLOR_GREEN, curses.COLOR_BLACK),
            "food": (curses.COLOR_RED, curses.COLOR_BLACK),
            "wall": (curses.COLOR_WHITE, curses.COLOR_BLACK),
            "text": (curses.COLOR_WHITE, curses.COLOR_BLACK),
            "menu": (curses.COLOR_CYAN, curses.COLOR_BLACK),
            "highlight": (curses.COLOR_BLACK, curses.COLOR_CYAN),
            "quit": (curses.COLOR_RED, curses.COLOR_BLACK),
            "option": (curses.COLOR_YELLOW, curses.COLOR_BLACK),
            "score": (curses.COLOR_WHITE, curses.COLOR_BLACK),
            "bonus_timer": (curses.COLOR_BLUE, curses.COLOR_BLACK),
            "bonus_food": (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
            "border": (curses.COLOR_WHITE, curses.COLOR_BLACK),
        }
    },
    "custom_colors": { # Make sure all themes have all elements
       "snake": (curses.COLOR_GREEN, curses.COLOR_BLACK),
        "food": (curses.COLOR_RED, curses.COLOR_BLACK),
        "wall": (curses.COLOR_WHITE, curses.COLOR_BLACK),
        "text": (curses.COLOR_WHITE, curses.COLOR_BLACK),
        "menu": (curses.COLOR_CYAN, curses.COLOR_BLACK),
        "highlight": (curses.COLOR_BLACK, curses.COLOR_CYAN),
        "quit": (curses.COLOR_RED, curses.COLOR_BLACK),
        "option": (curses.COLOR_YELLOW, curses.COLOR_BLACK),
        "score": (curses.COLOR_WHITE, curses.COLOR_BLACK),
        "bonus_timer": (curses.COLOR_BLUE, curses.COLOR_BLACK),
        "bonus_food": (curses.COLOR_MAGENTA, curses.COLOR_BLACK),
        "border": (curses.COLOR_WHITE, curses.COLOR_BLACK),
    }
}

SNAKE_ART = [
    "███████╗███╗   ██╗ █████╗ ██╗  ██╗███████╗",
    "██╔════╝████╗  ██║██╔══██╗██║ ██╔╝██╔════╝",
    "███████╗██╔██╗ ██║███████║█████╔╝ █████╗  ",
    "╚════██║██║╚██╗██║██╔══██║██╔═██╗ ██╔══╝  ",
    "███████║██║ ╚████║██║  ██║██║  ██╗███████╗",
    "╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝"
]


SNAKE_SEGMENTS = { # Characters of the snake body
    "vertical": "║",
    "horizontal": "═",
    "top_right": "╝",
    "top_left": "╚",
    "bottom_right": "╗",
    "bottom_left": "╔",
    "head_up": "Λ",
    "head_down": "V",
    "head_left": "<",
    "head_right": ">",
    "tail_left": "<",
    "tail_right": ">",
    "tail_up": "^",
    "tail_down": "v",
}

FOOD_CHAR = "*"  # Appearance of the food
BONUS_FOOD_CHAR = "*" # Appearance of the bonus food
HORIZONTAL_BORDER_CHAR = "─" # Character for horizontal
VERTICAL_BORDER_CHAR = "│"
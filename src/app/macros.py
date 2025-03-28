import time
from pynput.keyboard import Controller as KeyboardController, Key, Listener

# from pynput import keyboard
from keyboard import keyboard_controller


def tap_key(key):
    keyboard_controller.press(key)
    keyboard_controller.release(key)


def tap_undo():
    keyboard_controller.press(Key.ctrl)
    keyboard_controller.press("z")
    keyboard_controller.release("z")
    keyboard_controller.release(Key.ctrl)


def tab_ctrlenter():
    keyboard_controller.press(Key.ctrl),
    keyboard_controller.press(Key.enter),
    keyboard_controller.release(Key.enter),
    keyboard_controller.release(Key.ctrl)


def type_todays_date():
    today = datetime.now().strftime("%Y-%m-%d")
    keyboard_controller.type(today)


def type_current_time():
    current_time = datetime.now().strftime("%-I:%M%p").lower()
    keyboard_controller.type(current_time)


def type_current_time_and_date():
    type_todays_date()
    keyboard_controller.type(" @ ")
    type_current_time()  #


def tap_back_one_word():
    keyboard_controller.press(Key.ctrl)
    keyboard_controller.press(Key.shift)
    keyboard_controller.press(Key.left)

    keyboard_controller.release(Key.left)
    keyboard_controller.release(Key.shift)
    keyboard_controller.release(Key.ctrl)


def tap_delete():
    tap_key(Key.delete)
    tap_key(Key.space)


def type_delete_words(n):
    """
    Delete n words from the current text input.
    This is a simple implementation that types 'backspace' n times.
    """
    if n <= 0:
        return
    for _ in range(n):
        # Press backspace to delete one word

        # Optionally, you can add a small delay here if needed
        time.sleep(0.1)  # Adjust as necessary for your use case


MACROS = {
    "asterisk": "*",
    "atsign": "@",
    "spacebar": " ",
    "space": " ",
    "enter": "\n",
    "return": "\n",
    "newline": "\n",
    "up": lambda: tap_key(Key.up),
    "down": lambda: tap_key(Key.down),
    "left": lambda: tap_key(Key.left),
    "right": lambda: tap_key(Key.right),
    "escape": lambda: tap_key(Key.esc),
    "tab": lambda: tap_key(Key.tab),
    "end": lambda: tap_key(Key.end),
    "home": lambda: tap_key(Key.home),
    "pagedown": lambda: tap_key(Key.page_down),
    "pageup": lambda: tap_key(Key.page_up),
    "backspace": lambda: tap_key(Key.backspace),
    # Common punctuation and symbols
    "exclamationpoint": "!",
    "questionmark": "?",
    "period": ".",
    "comma": ",",
    "semicolon": ";",
    "colon": ":",
    "dash": "-",
    "underscore": "_",
    "delete": lambda: tap_delete(),
    # More advanced macros
    "undo": lambda: tap_undo(),
    "controlenter": lambda: tab_ctrlenter(),
    "backoneword": lambda: tap_back_one_word(),
    "todaysdate": lambda: type_todays_date(),
    "currenttime": lambda: type_current_time_and_date(),
    "currenttimeanddate": lambda: type_current_time_and_date(),
    # emoji
    "happyface": " :)",
    "sadface": " :(",
    "winkyface": " ;)",
    "grinningface": " :D",
}

MACRO_COMPLEX = {
    "delete#words": lambda n: type_delete_words(n),
}

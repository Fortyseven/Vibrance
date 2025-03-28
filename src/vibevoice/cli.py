"""Command-line interface for vibevoice"""

from rich import print
from rich.progress import Progress
import os
import subprocess
import time
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
import requests
from pynput.keyboard import Controller as KeyboardController, Key, Listener
from pynput import keyboard
from scipy.io import wavfile
from datetime import datetime
import sys

MIN_SAMPLES_FOR_TRANSCRIBE = 8000
VOICEKEY_DEFAULT = "shift_r" # + CTRL
RAW_MODE = False

keyboard_controller = None


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
    "delete#words": lambda n : type_delete_words(n),
}


def start_whisper_server():
    server_script = os.path.join(os.path.dirname(__file__), "server.py")
    process = subprocess.Popen(["python", server_script])
    return process


def wait_for_server(timeout=1800, interval=0.5):
    global keyboard_controller
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://localhost:4242/health")
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(interval)

    raise TimeoutError("Server failed to start within timeout")


def process_typed(text):
    if not RAW_MODE:
        sluggified = "".join(char for char in text.lower() if char.isalnum())

        for key, value in MACROS.items():
            if sluggified == key:

                if callable(value):
                    # If the value is a callable function, execute it
                    # This allows for special keys like 'up', 'down', etc.
                    print(f"Matched '{key}' in '{sluggified}' -> Executing function")
                    value()

                    text = ""
                else:
                    print(
                        f"Matched '{key}' in '{sluggified}' -> Replacing with '{value}'"
                    )
                    # Replace the matched key with its corresponding value
                    text = value
                    break

    if text:
        keyboard_controller.type(text)


def main():
    global keyboard_controller

    load_dotenv()
    RECORD_KEY = Key[VOICEKEY_DEFAULT]

    keyboard_controller = KeyboardController()

    recording = False
    audio_data = []
    sample_rate = 16000

    pressed_ctrl = False

    progress = Progress()
    progress_current = None

    def on_press(key):
        nonlocal recording, audio_data, pressed_ctrl, progress_current

        if key == Key.ctrl_r:
            pressed_ctrl = True
        elif key == RECORD_KEY and pressed_ctrl:
            recording = True
            audio_data = []

            progress.start()
            progress_current = progress.add_task(
                "[green bold]Recording...[/bold green]", total=None
            )
            progress.start_task(progress_current)

    def on_release(key):
        nonlocal recording, audio_data, pressed_ctrl, progress_current

        if key == Key.ctrl_r:
            pressed_ctrl = False

        if key == RECORD_KEY and recording:
            recording = False
            progress.stop_task(progress_current)
            progress.remove_task(progress_current)

            print("\r", end="")

            progress_current = progress.add_task(
                "[yellow bold]Transcribing...[/bold yellow]", total=None
            )

            try:
                audio_data_np = np.concatenate(audio_data, axis=0)
            except ValueError as e:
                print(e)
                return

            recording_path = os.path.abspath("recording.wav")
            audio_data_int16 = (audio_data_np * np.iinfo(np.int16).max).astype(np.int16)

            if audio_data_int16.shape[0] < MIN_SAMPLES_FOR_TRANSCRIBE:
                # Ensure there's enough data for Whisper to process
                print("[yellow]>>> (Ignoring short response.)[/yellow]")
                progress.remove_task(progress_current)
                progress.stop()
                return

            wavfile.write(recording_path, sample_rate, audio_data_int16)

            try:
                response = requests.post(
                    "http://localhost:4242/transcribe/",
                    json={"file_path": recording_path},
                )
                response.raise_for_status()
                transcript = response.json()["text"]

                if transcript:
                    processed_transcript = transcript  # + " "
                    print(
                        f'[yellow bold]>>>[/bold yellow] [white bold]"{processed_transcript}"[/bold white]'
                    )
                    process_typed(processed_transcript)

            except requests.exceptions.RequestException as e:
                print(f"[red]Error sending request to local API:[/red] {e}")
            except Exception as e:
                print(f"[red]Error processing transcript:[/red] {e}")
            finally:
                progress.remove_task(progress_current)
                progress.stop()

                print("\r" + " " * 15, end="\r")  # Clear the line to avoid overlap

    def callback(indata, frames, time, status):
        if status:
            print(status)
        if recording:
            audio_data.append(indata.copy())

    server_process = start_whisper_server()

    try:
        print(f"[yellow]Waiting for the server to be ready...[/yellow]")
        wait_for_server()
        print(
            f"[green]Transcriber is active. Hold down CTRL+SHIFT to start dictating.[/green]"
        )
        with Listener(on_press=on_press, on_release=on_release) as listener:
            with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate):
                listener.join()
    except TimeoutError as e:
        print(f"[red]Error: {e}[/red]")
        server_process.terminate()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[yellow]Stopping...[/yellow]")
    finally:
        server_process.terminate()


if __name__ == "__main__":
    main()

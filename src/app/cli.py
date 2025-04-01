"""Command-line interface for vibevoice"""

import os
import subprocess
import requests
import time
from rich import print
from rich.progress import Progress
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
import sys
import argparse

from pynput.keyboard import Controller as KeyboardController, Key, Listener

from keyboard import keyboard_controller

from macros import MACROS

MIN_SAMPLES_FOR_TRANSCRIBE = 8000
VOICEKEY_DEFAULT = "shift_r"  # + CTRL

DEFAULT_HOST = "http://localhost"
DEFAULT_PORT = 4242
SERVER_HOST = f"{DEFAULT_HOST}:{DEFAULT_PORT}"


def parse_arguments():
    """
    Parses command-line arguments for the CLI.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Command-line interface for vibevoice")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="Server host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Server port")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["code", "raw"],
        default="default",
        help="Set the transcription mode (code or raw)",
    )
    parser.add_argument(
        "--no-space",
        "-ns",
        action="store_true",
        help="Disable adding a space after transcriptions",
    )
    parser.add_argument("--cpu", action="store_true", help="Force server to run on CPU")
    return parser.parse_args()


def start_whisper_server(cpu=False):
    server_script = os.path.join(os.path.dirname(__file__), "server/server.py")
    command = ["python", server_script]
    if cpu:
        command.append("--cpu")
    process = subprocess.Popen(command)

    return process


def wait_for_server(timeout=1800, interval=0.5):
    """
    Waits for a server to become available by periodically sending a health check request.

    Args:
        timeout (int, optional): The maximum time to wait for the server to start, in seconds. Defaults to 1800 seconds (30 minutes).
        interval (float, optional): The time interval between consecutive health check requests, in seconds. Defaults to 0.5 seconds.

    Returns:
        bool: True if the server becomes available within the timeout period.

    Raises:
        TimeoutError: If the server does not become available within the specified timeout period.
    """

    global keyboard_controller

    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{SERVER_HOST}/health", timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(interval)

    raise TimeoutError("Server failed to start within timeout")


def process_typed(text, args):
    """
    Processes the given text input, applying transformations or executing macros
    based on predefined rules.
    Args:
        text (str): The input text to be processed.
        args (argparse.Namespace): Parsed command-line arguments.
    Behavior:
        - If mode is "raw":
            - Converts the input text to lowercase and removes non-alphanumeric characters.
            - Checks if the processed text matches any key in the MACROS dictionary.
            - If a match is found:
                - If the corresponding value is callable, executes the function and clears the text.
                - Otherwise, replaces the text with the corresponding value from the MACROS dictionary.
        - If mode is "code":
            - [Stubbed functionality for code mode].
        - If no match is found, the original or modified text is typed using
          the `keyboard_controller`.
    """

    if args.mode == "default":
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

    elif args.mode == "code":
        # Stub for code mode functionality
        print("[blue]Code mode is not yet implemented.[/blue]")

    if text:
        keyboard_controller.type(text)


def main():
    global keyboard_controller, SERVER_HOST

    args = parse_arguments()
    SERVER_HOST = f"{args.host}:{args.port}"
    add_space = not args.no_space

    # Pass the --cpu flag to the server process if specified
    server_process = start_whisper_server(cpu=args.cpu)

    RECORD_KEY = Key[VOICEKEY_DEFAULT]

    recording = False
    audio_data = []
    sample_rate = 16000

    pressed_ctrl = False
    pressed_shift = False

    progress = Progress()
    progress_current = None

    def on_press(key):
        """
        Handles key press events to control the recording process.
        This function listens for specific key combinations and updates the state
        of the recording process. It checks for the right control key (`Key.ctrl_r`)
        and the right shift key (`Key.shift_r`). When both keys are pressed
        simultaneously, it starts recording by setting the `recording` flag to True,
        initializes the `audio_data` list, stops any ongoing progress display, and
        starts a new progress display indicating that recording is in progress.

        Args:
            key: The key event object representing the key that was pressed.
        """

        nonlocal recording, audio_data, pressed_ctrl, pressed_shift

        if key == Key.ctrl_r:
            pressed_ctrl = True

        if key == Key.shift_r:
            pressed_shift = True

        if pressed_ctrl and pressed_shift:
            recording = True
            audio_data = []

            stop_progress()

            start_progress("[green bold]Recording...[/bold green]")

    def on_release(key):
        """
        Handles the release of keyboard keys during the recording process.

        This function is triggered when a key is released and performs the following:
        - Updates the state of `pressed_ctrl` and `pressed_shift` when the respective keys are released.
        - Stops the recording process if the `RECORD_KEY` is released without both `pressed_shift` and `pressed_ctrl` being active.
        - Processes the recorded audio data, saves it as a WAV file, and sends it to a transcription server.
        - Handles transcription responses and processes the resulting text.

        Args:
            key: The key that was released.

        Notes:
            - The function uses nonlocal variables: `recording`, `audio_data`, `pressed_shift`, and `pressed_ctrl`.
            - Ensures that the recorded audio has a minimum length before attempting transcription.
            - Handles exceptions during audio processing and transcription requests gracefully.
        """
        nonlocal recording, audio_data, pressed_shift, pressed_ctrl

        if key == Key.ctrl_r:
            pressed_ctrl = False

        if key == Key.shift_r:
            pressed_shift = False

        if recording and (pressed_shift == False and pressed_ctrl == False):
            recording = False

            stop_progress()

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
                stop_progress()
                return

            wavfile.write(recording_path, sample_rate, audio_data_int16)

            try:
                start_progress("[yellow bold]Transcribing...[/bold yellow]")

                response = requests.post(
                    f"{SERVER_HOST}/transcribe",
                    json={"file_path": recording_path},
                )
                response.raise_for_status()
                transcript = response.json()["text"]

                if transcript:
                    processed_transcript = transcript
                    if add_space:
                        processed_transcript += " "
                    print(
                        f'[yellow bold]>>>[/bold yellow] [white bold]"{processed_transcript}"[/bold white]'
                    )
                    process_typed(processed_transcript, args)

            except requests.exceptions.RequestException as e:
                print(f"[red]Error sending request to local API:[/red] {e}")
            except Exception as e:
                print(f"[red]Error processing transcript:[/red] {e}")
            finally:
                stop_progress()
                pressed_shift = False
                pressed_ctrl = False

    def stop_progress():
        nonlocal progress_current

        if progress_current:
            print("stopping progress", progress_current)
            progress.remove_task(progress_current)
            progress.stop()

        progress_current = None
        print("\r", end="")

    def start_progress(label: str):
        nonlocal progress_current

        stop_progress()

        progress.start()
        progress_current = progress.add_task(label, total=None)
        # progress.start_task(progress_current)

    def input_stream_callback(indata, frames, time, status):
        if status:
            print(status)
        if recording:
            audio_data.append(indata.copy())

    try:
        print(f"[yellow]Waiting for the server to be ready...[/yellow]")
        wait_for_server()
        print(
            f"[green]Transcriber is active. Hold down CTRL+SHIFT to start dictating.[/green]"
        )
        with Listener(on_press=on_press, on_release=on_release) as listener:
            with sd.InputStream(
                callback=input_stream_callback, channels=1, samplerate=sample_rate
            ):
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

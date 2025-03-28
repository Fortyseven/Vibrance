"""Command-line interface for vibevoice"""

import os
import subprocess
import time
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
import requests
from pynput.keyboard import Controller as KeyboardController, Key, Listener
from scipy.io import wavfile
import sys

MIN_SAMPLES_FOR_TRANSCRIBE = 8000
VOICEKEY_DEFAULT = "shift_r"  # old default "ctrl_r"
RAW_MODE = False

SUBS = {
    'asterisk': '*',
    'at sign': '@',
    'space.': ' ',
    'space bar': ' ',
    'spacebar': ' ',
    'enter': '\n',
    'enter.': '\n',
    'return': '\n',
    'new line': '\n',
    'backspace': chr(8),
}

keyboard_controller = None


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
        # Process the lower case text for substitutions
        lower_text = text.lower()
        matched = False
        for key, value in SUBS.items():
            if lower_text == key:
                print(f"Matched '{key}' in '{lower_text}' -> Replacing with '{value}'")
                # Replace the matched key with its corresponding value
                text = value
                matched = True
                break

    keyboard_controller.type(text)


def main():
    global keyboard_controller

    load_dotenv()
    key_label = os.environ.get("VOICEKEY", VOICEKEY_DEFAULT)
    RECORD_KEY = Key[key_label]

    keyboard_controller = KeyboardController()

    recording = False
    audio_data = []
    sample_rate = 16000

    pressed_ctrl = False

    def on_press(key):
        nonlocal recording, audio_data, pressed_ctrl

        if key == Key.ctrl_r:
            pressed_ctrl = True
        elif key == RECORD_KEY and pressed_ctrl:
            recording = True
            audio_data = []
            print("Listening...")

    def on_release(key):
        nonlocal recording, audio_data, pressed_ctrl

        if key == Key.ctrl_r:
            pressed_ctrl = False

        if key == RECORD_KEY and recording:
            recording = False
            print("Transcribing...")

            try:
                audio_data_np = np.concatenate(audio_data, axis=0)
            except ValueError as e:
                print(e)
                return

            recording_path = os.path.abspath("recording.wav")
            audio_data_int16 = (audio_data_np * np.iinfo(np.int16).max).astype(np.int16)

            if audio_data_int16.shape[0] < MIN_SAMPLES_FOR_TRANSCRIBE:
                # Ensure there's enough data for Whisper to process
                print("Ignoring short response.")
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
                    processed_transcript = transcript # + " "
                    print(f'>>> "{processed_transcript}"')
                    process_typed(processed_transcript)

            except requests.exceptions.RequestException as e:
                print(f"Error sending request to local API: {e}")
            except Exception as e:
                print(f"Error processing transcript: {e}")

    def callback(indata, frames, time, status):
        if status:
            print(status)
        if recording:
            audio_data.append(indata.copy())

    server_process = start_whisper_server()

    try:
        print(f"Waiting for the server to be ready...")
        wait_for_server()
        print(f"vibevoice is active. Hold down {key_label} to start dictating.")
        with Listener(on_press=on_press, on_release=on_release) as listener:
            with sd.InputStream(callback=callback, channels=1, samplerate=sample_rate):
                listener.join()
    except TimeoutError as e:
        print(f"Error: {e}")
        server_process.terminate()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        server_process.terminate()


if __name__ == "__main__":
    main()

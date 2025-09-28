import os
import subprocess

# from rich import print
# from rich.progress import Progress
# from rich.console import Console
# from rich.text import Text
import numpy as np
import sounddevice as sd
from scipy.io import wavfile
from datetime import datetime

from pynput.keyboard import Controller as KeyboardController, Key, Listener

from app.keyboard import keyboard_controller
from app.macros import MACROS


class VibranceCore:
    server_process = None

    def __init__(self, input_device=None):
        self.input_device = input_device

    def start_server(self, cpu=False, model=None):
        server_script = os.path.join(os.path.dirname(__file__), "server/server.py")
        command = ["python", server_script]
        if cpu:
            command.append("--cpu")
        command.append("--model=" + (model if model else "small"))
        process = subprocess.Popen(command)

        self.server_process = process

    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()  # Ensure the process is fully terminated


def list_input_devices():
    """Lists all available input devices."""
    print("Available input devices:")
    for idx, device in enumerate(sd.query_devices()):
        if device["max_input_channels"] > 0:
            print(f"{idx}: {device['name']}")

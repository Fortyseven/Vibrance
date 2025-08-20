#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import messagebox
import threading
import requests
import time
from rich.console import Console
from rich.text import Text
import sounddevice as sd
import numpy as np
from scipy.io import wavfile
from pynput.keyboard import Key
from app.keyboard import keyboard_controller
from app.macros import MACROS
from pyperclip import paste as clipboard_paste

class VibranceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Vibrance GUI")

        # Configuration Section
        config_frame = ttk.LabelFrame(root, text="Configuration")
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(config_frame, text="Host:").grid(row=0, column=0, sticky="w")
        self.host_entry = ttk.Entry(config_frame)
        self.host_entry.insert(0, "http://localhost")
        self.host_entry.grid(row=0, column=1, sticky="ew")

        ttk.Label(config_frame, text="Port:").grid(row=1, column=0, sticky="w")
        self.port_entry = ttk.Entry(config_frame)
        self.port_entry.insert(0, "4242")
        self.port_entry.grid(row=1, column=1, sticky="ew")

        ttk.Label(config_frame, text="Mode:").grid(row=2, column=0, sticky="w")
        self.mode_combobox = ttk.Combobox(config_frame, values=["default", "raw", "code", "llm"])
        self.mode_combobox.set("default")
        self.mode_combobox.grid(row=2, column=1, sticky="ew")

        ttk.Label(config_frame, text="Typing Delay:").grid(row=3, column=0, sticky="w")
        self.typing_delay_entry = ttk.Entry(config_frame)
        self.typing_delay_entry.insert(0, "0.01")
        self.typing_delay_entry.grid(row=3, column=1, sticky="ew")

        # Output Panel
        output_frame = ttk.LabelFrame(root, text="Transcription Output")
        output_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=15)
        self.output_text.grid(row=0, column=0, sticky="nsew")

        # Control Buttons
        control_frame = ttk.Frame(root)
        control_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_transcription)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_transcription, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Configure grid weights
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

        self.server_process = None
        self.recording = False
        self.audio_data = []
        self.sample_rate = 16000

    def start_transcription(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Start server and transcription in a separate thread
        threading.Thread(target=self.run_transcription, daemon=True).start()

    def stop_transcription(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.recording = False

        if self.server_process:
            self.server_process.terminate()

    def run_transcription(self):
        try:
            self.recording = True
            self.output_text.insert(tk.END, "Waiting for the server to be ready...\n")

            # Simulate server start and transcription process
            time.sleep(2)  # Replace with actual server start logic

            self.output_text.insert(tk.END, "Transcriber is active.\n")
            self.output_text.see(tk.END)

            # Simulate transcription process
            while self.recording:
                time.sleep(1)  # Replace with actual transcription logic
                self.output_text.insert(tk.END, "[Transcription] Example output...\n")
                self.output_text.see(tk.END)

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.stop_transcription()

if __name__ == "__main__":
    root = tk.Tk()
    app = VibranceGUI(root)
    root.mainloop()
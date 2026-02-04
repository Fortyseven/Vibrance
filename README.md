# Vibrance

[Demo w/ Audio](https://github.com/user-attachments/assets/1d989be6-9f00-4b2a-b5c0-240a554bc1ae)


Vibrance is a voice-to-text transcription tool powered by a local Whisper model. It allows users to dictate text, execute macros, and even generate code or interact with an Ollama LLM using voice commands.

This is a fork of https://github.com/mpaepper/vibevoice. It's been heavily modified and designed to fit my personal use cases, versus being user-friendly.

Out of the box it uses the right-hand CTRL+SHIFT combo as the push-to-talk trigger. You can change this to whatever you want, but you'll have to rig it up yourself.

This is incredibly slow if you use CPU.

## Features

- **Voice-to-Text Transcription**: Converts spoken words into text using a local Whisper model.
- **Macros**: Supports one-word or phrase macros for quick actions like typing the current date or navigating text.
- **LLM Integration**: Includes modes for interacting with an LLM or generating code snippets using Ollama.
- **Push-to-Talk & Toggle Recording**: Uses a customizable key combination (default: `CTRL+SHIFT`) to start and stop recording. Supports both hold-to-record and toggle modes.
- **Customizable Modes**:
  - `default`: Processes text with macros.
  - `raw`: Outputs raw transcriptions without processing.
  - `llm`: Interacts with an LLM for conversational responses.
  - `code`: Generates code snippets using an LLM.

## Requirements

- Python 3.8 or higher
- CUDA-compatible GPU (strongly recommended)
- Dependencies listed in `requirements.txt`

## Installation

Non-Linux installation is untested and is an exercise for the reader.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vibrance.git
   cd vibrance
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running Vibrance

1. Start the Vibrance client:
   ```bash
   python vibrance.py
   ```

   The transcription server will be launched automatically at runtime.

   Without arguments this launches in a default transcription mode with macro shortcuts, etc.

2. Hold down `CTRL+SHIFT` to start dictating. Release the keys to stop recording.

### Recording Modes

Vibrance supports two recording modes:

- **Hold Mode (default)**: Press and hold `CTRL+SHIFT` to record. Release both keys to stop recording and begin transcription.
- **Toggle Mode**: Press `CTRL+SHIFT` once to start recording, press again to stop recording and begin transcription. Enable with `--toggle-recording`.

### Command-Line Options

- `--host`: Specify the server host (default: `http://localhost`).
- `--port`: Specify the server port (default: `4242`).
- `--mode`: Set the transcription mode (`default`, `raw`, `code`, `llm`).
- `--no-space` or `-ns`: Disable adding a space after transcriptions.
- `--cpu`: Force using CPU for transcription (this is often unusably slow).
- `--toggle-recording`: Enable toggle mode for recording (press once to start, press again to stop).
- `--model`: Specify the Whisper model size (`tiny`, `base`, `small`, `medium`, `large`, `large-v2`).
- `--copy-selection`: Copy selected text before transcription (only available with `llm` or `code` modes).
- `--typing-delay`: Set the typing delay between keypresses in seconds (default: `0.01`).
- `--input-device`: Specify the input device index.
- `--list-devices`: List available input devices.

### Examples

To run the client in `code` mode:
```bash
python vibrance.py --mode code
```

To use toggle recording mode instead of hold-to-record:
```bash
python vibrance.py --toggle-recording
```

To use toggle mode with LLM integration:
```bash
python vibrance.py --mode llm --toggle-recording
```

### Adding Macros

Macros are defined in `app/macros.py`. Add new entries to the `MACROS` dictionary:
```python
MACROS = {
    ...existing code...
    "greet": "Hello, world!",
    "datetime": lambda: type_current_time_and_date(),
}
```

### LLM and Code Generation

The LLM and code generation modes use the `ollama` library. You can customize the model and temperature in `app/mode/llm.py` and `app/mode/code.py`.

NOTE: Like the rest of this project, this part is still a work in progress; one notable issue: code snippets tend to have indentation issues in VSCode and other editors that maintain consistent tab indents.

## TODO

- Swap Ollama support for a generic OpenAI endpoint (that Ollama also supports).

## Contributing

This project is not open for contributions. However, feel free to fork it and make your own modifications. This may change down the line, but for now I'm working on this solo in my spare time for fun.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- [Vibevoice](https://github.com/mpaepper/vibevoice) for the original implementation.
- [Ollama](https://ollama.ai/) for LLM integration.
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) for efficient transcription.
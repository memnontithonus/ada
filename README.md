# ADA (Advanced Design Assistant)

ADA is a helpful AI assistant specializing in STEM fields, designed to provide concise and accurate information and assist with various tasks through voice or text interaction. ADA comes in two versions: a local version (`ada_local`) that runs primarily on your machine and an online version (`ada_online`) that utilizes cloud-based services.

## Features

* **Dual Versions:** Choose between running ADA locally or using online services.
* **Real-time Interaction:** Communicate with ADA using voice (Speech-to-Text) and receive spoken responses (Text-to-Speech).
* **Function Calling:** ADA can perform specific tasks by calling available functions (widgets), such as:
    * Accessing system information (`system.info`)
    * Setting timers (`timer.set`)
    * Creating project folders (`project.create_folder`)
    * Opening the camera (`camera.open`)
    * Managing a To-Do list (`to_do_list.create_list`, `add_task`, etc.)
* **STEM Expertise:** Designed to assist with engineering, math, and science queries.
* **Conversational:** Engages in natural language conversation.

## Setup

### Prerequisites

* **Python:** Ensure you have Python installed (the code appears to use features compatible with Python 3.11+).
* **Ollama (for `ada_local`):** You need Ollama installed and running to serve the local LLM. Make sure you have downloaded the model specified in `ADA_Local.py` (e.g., `gemma3:1b-it-q4_K_M` or similar).
* **CUDA (Optional, for `ada_local`):** For better performance with local models, a CUDA-compatible GPU and the necessary drivers are recommended. ADA will automatically detect and use the GPU if available via PyTorch.
* **Microphone and Speakers:** Required for voice interaction (STT/TTS).
* **API Keys (for `ada_online`):** See the API Key Setup section below.

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd ada_v1
    ```
2.  **Install Dependencies:**
    Install the required Python libraries. Based on the imports in the provided files, you'll likely need:
    ```bash
    pip install ollama websockets pyaudio RealtimeSTT RealtimeTTS torch google-generativeai opencv-python pillow mss psutil GPUtil elevenlabs python-dotenv # Add any other specific libraries used
    ```
    *Note: Installing `PyAudio` might require additional system dependencies (like `portaudio`). `CoquiEngine` within `RealtimeTTS` might also have specific installation steps.*
    *Note: The `realtimesst.log` file shows errors related to FFmpeg not being found by the `torio` library (a dependency likely used by `RealtimeTTS` or `RealtimeSTT`). Ensure FFmpeg is installed and accessible in your system's PATH if you encounter audio processing issues.*

## API Key Setup (for `ada_online`)

The online version (`ada_online`) requires API keys for cloud services.

### 1. Google Generative AI (Gemini API)

* **Purpose:** Used for the core language model processing in `ada_online`.
* **How to get a key:**
    1.  Visit the Google AI Studio website: [https://aistudio.google.com/](https://aistudio.google.com/)
    2.  Sign in with your Google account.
    3.  Create a new API key. You might need to associate it with a Google Cloud project.
* **How to use the key:**
    1.  Open the `ADA/ADA_Online.py` file.
    2.  Locate the line where the `genai.Client` is initialized:
        ```python
        client = genai.Client(api_key="YOUR_API_KEY_HERE", http_options={'api_version': 'v1beta'})
        ```
    3.  Replace `"YOUR_API_KEY_HERE"` with the actual API key you generated.
    * **Security Note:** For better security, especially in production, consider using environment variables to store your API key instead of hardcoding it.

### 2. ElevenLabs

* **Purpose:** Used for Text-to-Speech (TTS) capabilities in `ada_online`.
* **How to get a key:**
    1.  Go to the ElevenLabs website: [https://elevenlabs.io/](https://elevenlabs.io/)
    2.  Log in to your account.
    3.  Navigate to your profile/settings page.
    4.  Find and copy your API key.
* **How to use the key:**
    1.  Open the `ADA/ADA_Online.py` file.
    2.  Locate the line defining `ELEVENLABS_API_KEY`:
        ```python
        ELEVENLABS_API_KEY = 'YOUR_API_KEY_HERE'
        ```
    3.  Replace `'YOUR_API_KEY_HERE'` with your actual ElevenLabs API key.

## Running ADA

### `ada_local`

This version uses Ollama for the language model and local engines for STT and TTS. Performance will depend on your hardware.

* **Real-time STT:** Uses the `RealtimeSTT` library.
* **Real-time TTS:** Uses the `RealtimeTTS` library, likely defaulting to the `SystemEngine` (using your OS's built-in TTS) or potentially `CoquiEngine` if configured.
* **To run:**
    ```bash
    python main_local.py
    ```
   

### `ada_online`

This version uses Google Gemini for the language model and ElevenLabs for TTS, relying on cloud services. It generally offers faster and potentially higher-quality responses but requires API keys and an internet connection.

* **Real-time STT:** Uses the `RealtimeSTT` library.
* **Real-time TTS:** Uses the `ElevenlabsEngine` via WebSockets.
* **To run:**
    ```bash
    python main_online.py
    ```
   

## Usage

Once running, you can interact with ADA either by typing your prompts into the console when prompted or by speaking (if using `ada_local` or `ada_online` with STT enabled).

* Press Enter after typing a message.
* Speak clearly into your microphone for voice input.
* Type `exit` and press Enter to quit the application.

## Widgets

ADA can utilize several built-in functions (widgets) located in the `WIDGETS/` directory:

* `camera.py`: Opens the default camera feed.
* `project.py`: Creates project folders.
* `system.py`: Provides system hardware information (CPU, RAM, GPU).
* `timer.py`: Sets countdown timers.
* `to_do_list.py`: Manages a simple to-do list.
* *Placeholder Widgets:* `z-calc.py`, `z-news.py`, `z-weather.py`, `z-world_clock.py`, `z-youtube_player.py` (These seem to be placeholders and currently just print their names).

ADA decides when to call these functions based on your request.

## Troubleshooting

* **Audio Issues:** Ensure your microphone and speakers are correctly configured as the system default. Check dependencies like `PyAudio`, `PortAudio`, and potentially `FFmpeg`.
* **API Key Errors:** Double-check that your API keys are correctly entered in `ADA_Online.py` and that they are active and have the necessary permissions/quota.
* **Library Errors:** Make sure all dependencies listed in `Setup` are installed correctly. Some libraries might have platform-specific requirements.
* **Ollama Issues (`ada_local`):** Confirm Ollama is running and the specified model is downloaded and accessible.

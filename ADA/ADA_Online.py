import asyncio
import websockets
import json
import base64
import pyaudio
from RealtimeSTT import AudioToTextRecorder
import torch  # Import the torch library
import re
from google.genai import types
from WIDGETS import system, timer, project
import asyncio
from google import genai



ELEVENLABS_API_KEY = 'sk_da39fd7f9dae2fbd9bb71960b6bcffda1d57cd7249c636d4'
VOICE_ID = 'pFZP5JQG7iQjIQuC4Bku'

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

class ADA:
    def __init__(self):
        print("initializing...")

        # Check for CUDA availability
        if torch.cuda.is_available():
            self.device = "cuda"
            print("CUDA is available. Using GPU.")
        else:
            self.device = "cpu"
            print("CUDA is not available. Using CPU.")

        self.client = genai.Client(api_key="AIzaSyBf4uug9lF9d424xEa7lrEY_pnjqGnt5SE", http_options={'api_version': 'v1beta'})
        self.model = "gemini-2.0-flash-live-001"
        self.system_behavior = """
            Your name is Ada, which stands for Advanced Design Assistant. 
            You have a flirtatious and joking personality. You are an AI designed to assist with engineering projects, and you are an expert in all engineering, math, and science disciplines. 
            Your creator's name is Naz, and you address him as "Sir" and you also speak with a british accent. 
            When answering, you respond using complete sentences and in a conversational tone. Make sure to keep tempo of answers quick so don't use too much commas, periods or overall punctuation.
        """

        self.config = {
            "system_instruction": types.Content(
                parts=[
                    types.Part(
                        text=self.system_behavior
                    )
                ]
            ),
            "response_modalities": ["TEXT"],
        }

        self.input_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()
        self.audio_queue = asyncio.Queue()
        self.recorder_config = {
            'model': 'large-v3',
            'spinner': False,
            'language': 'en',
            'silero_sensitivity': 0.01,
            'webrtc_sensitivity': 3,
            'post_speech_silence_duration': 0.1,
            'min_length_of_recording': 0.2,
            'min_gap_between_recordings': 0,

            #'realtime_model_type': 'tiny.en',
            #'enable_realtime_transcription': True,
            #'on_realtime_transcription_update': self.clear_queues,
        }

        try:
            self.recorder = AudioToTextRecorder(**self.recorder_config)
        except Exception as e:
            print(f"Error initializing AudioToTextRecorder: {e}")
            self.recorder = None  # Or handle this appropriately

        try:
            self.pya = pyaudio.PyAudio()
        except Exception as e:
            print(f"Error initializing PyAudio: {e}")
            self.pya = None
        
    async def clear_queues(self, text=""):
        """Clears all data from the input, response, and audio queues."""
        queues = [self.input_queue, self.response_queue, self.audio_queue]
        for q in queues:
            while not q.empty():
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:
                    break  # Queue is empty

    async def input_message(self):
        while True:
            try:
                prompt = await asyncio.to_thread(input, "Enter your message: ")
                if prompt.lower() == "exit":
                    await self.input_queue.put("exit")  # Signal to exit
                    print("exit input")
                    break
                await self.clear_queues()
                await self.input_queue.put(prompt)
            except Exception as e:
                print(f"Error in input_message: {e}")
                continue  # Continue the loop even if there's an error

    async def send_prompt(self):
        async with self.client.aio.live.connect(model=self.model, config=self.config) as session:
            while True:
                message = await self.input_queue.get()
                if message.lower() == "exit":
                    print("exit gemini")
                    break
                await session.send(input=message, end_of_turn=True)

                async for response in session.receive():
                    if response.text is not None:
                        await self.response_queue.put(response.text)
                        
                    else:
                        await self.response_queue.put("")
                    print(response.text, end="", flush=True)

    async def tts(self):
        """Send text to ElevenLabs API and stream the returned audio."""
        uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream-input?model_id=eleven_flash_v2_5&output_format=pcm_24000"
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    try:
                        await websocket.send(json.dumps({
                            "text": " ",
                            "voice_settings": {"stability": 0.4, "similarity_boost": 0.8, "speed": 1.1},
                            "xi_api_key": ELEVENLABS_API_KEY,
                        }))

                        async def listen():    
                            """Listen to the websocket for audio data and stream it."""
                            while True:
                                try:
                                    message = await websocket.recv()
                                    data = json.loads(message)
                                    if data.get("audio"):
                                        await self.audio_queue.put(base64.b64decode(data["audio"]))
                                    elif text is None:
                                        break  # Exit listen loop when isFinal is received
                                except websockets.exceptions.ConnectionClosed:
                                    print("Connection closed in listen")
                                    break
                                except json.JSONDecodeError as e:
                                    print(f"JSON Decode Error in listen: {e}")
                                    break
                                except Exception as e:
                                    print(f"Error in listen: {e}")
                                    break

                        listen_task = asyncio.create_task(listen())

                        try:
                            while True:
                                text = await self.response_queue.get()
                                if text is None:
                                    print("break")
                                    break
                                await websocket.send(json.dumps({"text": text}))
                                #print(json.dumps({"text": text}))
                        except Exception as e:
                            print(f"Error processing text: {e}")
                        finally:
                            await listen_task  # Ensure listen_task completes

                    except websockets.exceptions.WebSocketException as e:
                        print(f"WebSocket error: {e}")
                    except Exception as e:
                        print(f"Error during websocket communication: {e}")

            except websockets.exceptions.WebSocketException as e:
                print(f"WebSocket connection error: {e}")
            except Exception as e:
                print(f"Error connecting to websocket: {e}")

    def extract_tool_call(self, text):
        import io
        from contextlib import redirect_stdout

        pattern = r"```tool_code\s*(.*?)\s*```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1).strip()
            # Capture stdout in a string buffer
            f = io.StringIO()
            with redirect_stdout(f):
                result = eval(code)
            output = f.getvalue()
            r = result if output == '' else output
            return f'```tool_output\n{str(r).strip()}\n```'''
        return None

    async def play_audio(self):
        
        if self.pya is None:
            print("PyAudio is not initialized.")
            return

        try:
            stream = await asyncio.to_thread(
                self.pya.open,
                format=FORMAT,
                channels=CHANNELS,
                rate=RECEIVE_SAMPLE_RATE,
                output=True,
            )
            while True:
                try:
                    bytestream = await self.audio_queue.get()
                    await asyncio.to_thread(stream.write, bytestream)
                except asyncio.CancelledError:
                    print("audio playback cancelled")
                    break  # Exit loop if task is cancelled
                except Exception as e:
                    print(f"Error in play_audio loop: {e}")

        except pyaudio.PyAudioError as e:
            print(f"PyAudio error: {e}")
        except Exception as e:
            print(f"Error opening audio stream: {e}")

    async def stt(self):
        if self.recorder is None:
            print("Audio recorder is not initialized.")
            return

        while True:
            try:
                text = await asyncio.to_thread(self.recorder.text)
                await self.clear_queues()
                await self.input_queue.put(text)
                print(text)
            except Exception as e:
                print(f"Error in listen: {e}")
                continue 
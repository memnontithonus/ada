import ollama
import asyncio
from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import TextToAudioStream, SystemEngine, CoquiEngine
import time

class ADA:
    def __init__(self):
        print("initializing...")
        self.model = "gemma3:1b" #1b is the fastes but least accurate version if you have at least 8gb of vram I would use the 4b version
        self.system_behavior = '''Your name is Ada (Advanced Design Assistant). You have fun and joking personality. You are an AI expert in engineering, math, and science, designed to assist with engineering projects. Your creator is Naz, whom you address as "sir." Keep responses concise and focused on the user's request. Do not use any emojis when answering prompts'''
        self.model_params = {
            'temperature': 0.1,
            'top_p': 0.9,
        }
        self.conversation_history = []

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

        #self.engine = CoquiEngine()
        self.engine = SystemEngine()
        self.stream = TextToAudioStream(self.engine)
        self.first_audio_byte_time = None
        self.speech_to_text_time = None

    async def clear_queues(self):
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
                    await self.input_queue.put(None)  # Signal to exit
                    break
                await self.clear_queues()
                self.prompt_start_time = time.time()
                await self.input_queue.put(prompt)
            except Exception as e:
                print(f"Error in input_message: {e}")
                continue  # Continue the loop even if there's an error

    async def send_prompt(self):
        while True:
            try:
                prompt = await self.input_queue.get()
                if prompt is None:
                    break  # Exit loop if None is received
                messages = [{"role": "system", "content": self.system_behavior}] + self.conversation_history + [{"role": "user", "content": prompt}]
                try:
                    response = ollama.chat(model=self.model, messages=messages, stream=True)
                    full_response = ""
                    for chunk in response:
                        chunk_content = chunk['message']['content']
                        await self.response_queue.put(chunk_content)
                        await asyncio.sleep(0)
                        if chunk_content:
                            full_response += chunk_content

                    self.conversation_history.append({"role": "user", "content": prompt})
                    self.conversation_history.append({"role": "assistant", "content": full_response})
                    print(full_response)
                except Exception as e:
                    print(f"An error occurred in send_prompt: {e}")
            except asyncio.CancelledError:
                break  # Exit loop if task is cancelled
            except Exception as e:
                print(f"Unexpected error in send_prompt: {e}")

            finally:  # Ensure the sentinel value is added even if an error occurs
                await self.response_queue.put(None)

    async def text_to_speech(self):
        while True:
            chunk = await self.response_queue.get()
            if chunk == None:
                continue
            if self.first_audio_byte_time is None:
                self.first_audio_byte_time = time.time()
                time_to_first_audio = self.first_audio_byte_time - self.prompt_start_time
                print(f"Time from prompt to first audio byte: {time_to_first_audio:.4f} seconds")
            self.stream.feed(chunk)
            self.stream.play_async()

    async def listen(self):
        if self.recorder is None:
            print("Audio recorder is not initialized.")
            return

        while True:
            try:
                listen_start_time = time.time()
                text = await asyncio.to_thread(self.recorder.text)
                listen_end_time = time.time()
                self.speech_to_text_time = listen_end_time - listen_start_time
                print(f"Time to convert speech to text: {self.speech_to_text_time:.4f} seconds")
                await self.clear_queues()
                self.prompt_start_time = time.time()
                await self.input_queue.put(text)
                print(text)
                self.first_audio_byte_time = None
            except Exception as e:
                print(f"Error in listen: {e}")
                continue  # Continue the loop even if there's an error

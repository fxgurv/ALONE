import os
import sys
import io
import warnings
from typing import Optional
from contextlib import redirect_stdout, redirect_stderr
import requests
from termcolor import colored
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTS:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.local_ai_url = os.getenv('LOCAL_AI_URL', 'https://imseldrith-tts-openai-free.hf.space/v1/audio/speech')
        
        # Voice collections
        self.openai_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        
        self.edge_voices = [
            "en-US-ChristopherNeural", "en-US-EricNeural", "en-US-GuyNeural",
            "en-US-JennyNeural", "en-US-AriaNeural", "en-US-DavisNeural",
            "en-US-MonicaNeural", "en-US-SaraNeural", "en-US-AnaNeural",
            "en-GB-LibbyNeural", "en-GB-MaisieNeural", "en-GB-RyanNeural",
            "en-GB-SoniaNeural", "en-GB-ThomasNeural"
        ]
        
        self.elevenlabs_voices = {
            "Rachel": "21m00Tcm4TlvDq8ikWAM",
            "Domi": "AZnzlk1XvdvUeBnXmlld",
            "Bella": "EXAVITQu4vr4xnSDxMaL",
            "Antoni": "ErXwobaYiN019PkySvjV",
            "Elli": "MF3mGyEYCl7XYWbV9V6O",
            "Josh": "TxGEqnHWrfWFTfGW9XjX",
            "Arnold": "VR6AewLTigWG4xSOukaG",
            "Adam": "pNInz6obpgDQGcFmaJgB",
            "Sam": "yoZ06aMxZJJ28mfd3POQ"
        }

        self.google_langs = {
            "English": "en", "Spanish": "es", "French": "fr",
            "German": "de", "Italian": "it", "Portuguese": "pt",
            "Russian": "ru", "Japanese": "ja", "Korean": "ko",
            "Chinese": "zh-CN", "Hindi": "hi"
        }

    def select_voice(self, tts_type):
        if tts_type == "openai":
            print("\nAvailable OpenAI voices:")
            for i, voice in enumerate(self.openai_voices, 1):
                print(f"{i}. {voice}")
            choice = int(input("\nSelect voice number: ")) - 1
            return self.openai_voices[choice]
            
        elif tts_type == "edge":
            print("\nAvailable Edge TTS voices:")
            for i, voice in enumerate(self.edge_voices, 1):
                print(f"{i}. {voice}")
            choice = int(input("\nSelect voice number: ")) - 1
            return self.edge_voices[choice]
            
        elif tts_type == "elevenlabs":
            print("\nAvailable ElevenLabs voices:")
            voices = list(self.elevenlabs_voices.keys())
            for i, voice in enumerate(voices, 1):
                print(f"{i}. {voice}")
            choice = int(input("\nSelect voice number: ")) - 1
            return voices[choice], self.elevenlabs_voices[voices[choice]]
            
        elif tts_type == "google":
            print("\nAvailable languages:")
            langs = list(self.google_langs.keys())
            for i, lang in enumerate(langs, 1):
                print(f"{i}. {lang}")
            choice = int(input("\nSelect language number: ")) - 1
            return self.google_langs[langs[choice]]

    def google_tts(self, text, output_file="google_tts_output.mp3"):
        from gtts import gTTS
        lang = self.select_voice("google")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_file)
        return output_file

    async def edge_tts(self, text, output_file="edge_tts_output.mp3"):
        import edge_tts
        voice = self.select_voice("edge")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        return output_file

    def openai_tts(self, text, output_file="openai_tts_output.mp3"):
        voice = self.select_voice("openai")
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "tts-1",
            "input": text,
            "voice": voice
        }
        response = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return output_file
        return None

    def local_ai_tts(self, text, output_file="local_ai_tts_output.mp3"):
        logger.info("Synthesizing text using Local AI TTS (imseldrith)")
        voice = self.select_voice("openai")  # Uses same voices as OpenAI
        headers = {
            "accept": "*/*",
            "Content-Type": "application/json"
        }
        data = {
            "model": "tts-1",
            "input": text,
            "voice": voice,
            "response_format": "mp3",
            "speed": 1
        }
        try:
            response = requests.post(
                self.local_ai_url,
                json=data,
                headers=headers
            )
            response.raise_for_status()

            with open(output_file, "wb") as f:
                f.write(response.content)

            logger.info(f"Audio synthesized successfully and saved to {output_file}")
            return output_file
        except requests.exceptions.RequestException as e:
            logger.error(f"Error with Local AI TTS: {str(e)}")
            return None

    def elevenlabs_tts(self, text, output_file="elevenlabs_tts_output.mp3"):
        voice_name, voice_id = self.select_voice("elevenlabs")
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return output_file
        return None

    def coqui_tts(self, text, output_file="coqui_tts_output.wav"):
        from TTS.api import TTS as CoquiTTS
        tts = CoquiTTS("tts_models/en/ljspeech/tacotron2-DDC")
        tts.tts_to_file(text=text, file_path=output_file)
        return output_file

    def mozilla_tts(self, text, output_file="mozilla_tts_output.wav"):
        from TTS.api import TTS as MozillaTTS
        tts = MozillaTTS("tts_models/en/ljspeech/mozilla-tts")
        tts.tts_to_file(text=text, file_path=output_file)
        return output_file

    def fairseq_tts(self, text, output_file="fairseq_tts_output.wav"):
        import torch
        import soundfile as sf
        from fairseq.checkpoint_utils import load_model_ensemble_and_task_from_hf_hub
        from fairseq.models.text_to_speech.hub_interface import TTSHubInterface
        
        models, cfg, task = load_model_ensemble_and_task_from_hf_hub(
            "facebook/fastspeech2-en-ljspeech"
        )
        model = models[0]
        TTSHubInterface.update_cfg_with_data_cfg(cfg, task.data_cfg)
        generator = task.build_generator([model], cfg)
        
        sample = TTSHubInterface.get_model_input(task, text)
        wav, rate = TTSHubInterface.get_prediction(task, model, generator, sample)
        sf.write(output_file, wav, rate)
        return output_file

def main():
    tts = TTS()
    options = [
        "Google TTS (Multiple Languages)",
        "Edge TTS (Multiple Voices)",
        "OpenAI TTS (Multiple Voices)",
        "Local AI TTS (imseldrith)",
        "Elevenlabs TTS (Multiple Voices)",
        "Coqui TTS",
        "Mozilla TTS",
        "Fairseq TTS",
        "Exit"
    ]

    while True:
        print(colored("\nText-to-Speech Options:", "cyan"))
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

        choice = input(colored("\nEnter your choice (1-9): ", "yellow"))

        if choice == "9":
            print(colored("Exiting...", "green"))
            break

        if choice in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            text = input(colored(f"\nEnter text for {options[int(choice)-1]}: ", "yellow"))
            
            try:
                if choice == "1":
                    output_file = tts.google_tts(text)
                elif choice == "2":
                    output_file = asyncio.run(tts.edge_tts(text))
                elif choice == "3":
                    output_file = tts.openai_tts(text)
                elif choice == "4":
                    output_file = tts.local_ai_tts(text)
                elif choice == "5":
                    output_file = tts.elevenlabs_tts(text)
                elif choice == "6":
                    output_file = tts.coqui_tts(text)
                elif choice == "7":
                    output_file = tts.mozilla_tts(text)
                elif choice == "8":
                    output_file = tts.fairseq_tts(text)

                if output_file:
                    print(colored(f"\nAudio generated and saved as {output_file}", "green"))
                else:
                    print(colored("Failed to generate audio", "red"))
            except Exception as e:
                print(colored(f"Error: {str(e)}", "red"))
        else:
            print(colored("Invalid choice. Please try again.", "red"))

if __name__ == "__main__":
    main()

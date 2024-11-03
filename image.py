import os, requests, logging, base64, time, json
from termcolor import colored
from random import randint
from requests.adapters import HTTPAdapter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.stability_api_key = os.getenv('STABILITY_API_KEY')
        self.leonardo_api_key = os.getenv('LEONARDO_API_KEY')
        
        # Available providers and models
        self.providers = {
            "1": "DALL-E (OpenAI)", "2": "Stability AI", "3": "Hercai",
            "4": "Leonardo AI", "5": "Prodia", "6": "Pollinations"
        }
        
        self.models = {
            "dalle": ["dall-e-2", "dall-e-3"],
            "stability": ["stable-diffusion-xl-1024-v1-0", "stable-diffusion-v1-6", "stable-diffusion-512-v2-1"],
            "hercai": ["v1", "v2", "v3", "lexica", "prodia", "simurg", "animefy", "raava", "shonin"],
            "prodia": ["blazing_drive_v10g.safetensors [ca1c1eab]", "dreamshaper_6BakedVae.safetensors [114c8abb]", 
                      "dreamlike-anime-1.0.safetensors [4520e090]"],
            "leonardo": {
                "sd-1.5": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",
                "sd-2.1": "ac614f96-1082-45bf-be9d-757f2d31c174",
                "creative": "cd2b2a15-9760-4174-a5ff-4d2925057376"
            }
        }

    def select_provider(self):
        print(colored("\nAvailable Image Providers:", "cyan"))
        for key, provider in self.providers.items():
            print(f"{key}. {provider}")
        
        choice = input(colored("\nSelect provider number: ", "yellow"))
        while choice not in self.providers:
            print(colored("Invalid choice. Please try again.", "red"))
            choice = input(colored("Select provider number: ", "yellow"))
        return choice

    def select_model(self, provider):
        if provider == "6": return None  # Pollinations doesn't need model selection
        
        model_map = {
            "1": "dalle", "2": "stability", "3": "hercai",
            "4": "leonardo", "5": "prodia"
        }
        
        model_list = self.models[model_map[provider]]
        print(f"\nAvailable models:")
        for i, model in enumerate(model_list if isinstance(model_list, list) else model_list.keys(), 1):
            print(f"{i}. {model}")
        
        while True:
            try:
                choice = int(input("\nSelect model number: ")) - 1
                if 0 <= choice < len(model_list):
                    if provider == "4":  # Leonardo
                        models = list(model_list.keys())
                        return models[choice], model_list[models[choice]]
                    return list(model_list)[choice]
            except ValueError:
                pass
            print(colored("Invalid choice. Please try again.", "red"))

    def dalle_generate(self, model, prompt, output_file="dalle_output.png"):
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"},
            json={"model": model, "prompt": prompt, "n": 1, "size": "1024x1024"}
        )
        
        if response.status_code == 200:
            img_data = requests.get(response.json()['data'][0]['url']).content
            with open(output_file, 'wb') as f:
                f.write(img_data)
            return output_file
        return None

    def stability_generate(self, model, prompt, output_file="stability_output.png"):
        response = requests.post(
            f"https://api.stability.ai/v1/generation/{model}/text-to-image",
            headers={"Authorization": f"Bearer {self.stability_api_key}", "Content-Type": "application/json"},
            json={"text_prompts": [{"text": prompt}], "cfg_scale": 7, "height": 1024, "width": 1024, "samples": 1}
        )
        
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(base64.b64decode(response.json()['artifacts'][0]['base64']))
            return output_file
        return None

    def hercai_generate(self, model, prompt, output_file="hercai_output.png"):
        response = requests.get(f"https://hercai.onrender.com/{model}/text2image?prompt={prompt}")
        data = response.json()
        
        if "url" in data and data["url"]:
            img_data = requests.get(data["url"]).content
            with open(output_file, 'wb') as f:
                f.write(img_data)
            return output_file
        return None

    def prodia_generate(self, model, prompt, output_file="prodia_output.png"):
        s = requests.Session()
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"}
        
        resp = s.get(
            "https://api.prodia.com/generate",
            params={
                "new": "true", "prompt": prompt, "model": model,
                "negative_prompt": "verybadimagenegative_v1.3",
                "steps": "20", "cfg": "7", "seed": randint(1, 10000),
                "sample": "DPM++ 2M Karras", "aspect_ratio": "square"
            },
            headers=headers
        )
        
        job_id = resp.json()['job']
        while True:
            time.sleep(5)
            status = s.get(f"https://api.prodia.com/job/{job_id}", headers=headers).json()
            if status["status"] == "succeeded":
                img_data = s.get(f"https://images.prodia.xyz/{job_id}.png?download=1", headers=headers).content
                with open(output_file, 'wb') as f:
                    f.write(img_data)
                return output_file
        return None

    def pollinations_generate(self, prompt, output_file="pollinations_output.png"):
        response = requests.get(f"https://image.pollinations.ai/prompt/{prompt}{randint(1, 10000)}")
        if response.status_code == 200:
            with open(output_file, 'wb') as f:
                f.write(response.content)
            return output_file
        return None

    def leonardo_generate(self, model_info, prompt, output_file="leonardo_output.png"):
        model_name, model_id = model_info
        headers = {"Authorization": f"Bearer {self.leonardo_api_key}", "Content-Type": "application/json"}
        
        response = requests.post(
            "https://cloud.leonardo.ai/api/rest/v1/generations",
            headers=headers,
            json={"prompt": prompt, "modelId": model_id, "num_images": 1, "width": 1024, "height": 1024}
        )
        
        if response.status_code == 200:
            generation_id = response.json()['generationId']
            while True:
                time.sleep(1)
                status = requests.get(
                    f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}",
                    headers=headers
                ).json()
                
                if status['status'] == 'COMPLETE':
                    img_data = requests.get(status['generations'][0]['imageUrl']).content
                    with open(output_file, 'wb') as f:
                        f.write(img_data)
                    return output_file
        return None

def main():
    generator = ImageGenerator()
    while True:
        provider = generator.select_provider()
        model = generator.select_model(provider)
        prompt = input(colored("\nEnter your prompt: ", "yellow"))
        
        generator_map = {
            "1": generator.dalle_generate,
            "2": generator.stability_generate,
            "3": generator.hercai_generate,
            "4": generator.leonardo_generate,
            "5": generator.prodia_generate,
            "6": generator.pollinations_generate
        }
        
        try:
            output_file = generator_map[provider](model, prompt) if provider != "6" else generator_map[provider](prompt)
            print(colored(f"\nImage {'generated and saved as ' + output_file if output_file else 'generation failed'}", "green" if output_file else "red"))
        except Exception as e:
            print(colored(f"Error: {str(e)}", "red"))
            
        if input(colored("\nGenerate another image? (y/n): ", "yellow")).lower() != 'y':
            break

if __name__ == "__main__":
    main()

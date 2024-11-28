import torch
from diffusers import StableDiffusionPipeline
from safetensors.torch import load_file

class ImageGenerator:
    """
    Class responsible for generating images using Stable Diffusion and PyTorch.
    """

    def __init__(self):
        """
        Initializes the ImageGenerator with the specified model checkpoint.

        Args:
            checkpoint_path (str): Path to the safetensors checkpoint file.
            device (str): The device to run the model on ('cuda', 'cpu', or 'mps').
        """
        # Device selection
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        checkpoint_path = "models/analogMadness_v70.safetensors"

        # Print the device being used
        if self.device.type == "cuda":
            print("Using GPU (CUDA) for image generation.")
        elif self.device.type == "mps":
            print("Using MPS (Apple Silicon) for image generation.")
        else:
            print("Using CPU for image generation.")

        # Load the Stable Diffusion pipeline
        self.pipe = StableDiffusionPipeline.from_single_file(
            checkpoint_path,
            use_safetensors=True,
            torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
        )

        # Load the custom weights from the checkpoint
        # self._load_custom_weights(checkpoint_path)

        # Move the pipeline to the selected device
        self.pipe.to(self.device)

        # Enable attention slicing to reduce memory usage
        self.pipe.enable_attention_slicing()

    def _load_custom_weights(self, checkpoint_path):
        """
        Load custom weights from a safetensors checkpoint.

        Args:
            checkpoint_path (str): Path to the safetensors checkpoint file.
        """
        print(f"Loading custom weights from {checkpoint_path}...")
        # Load safetensors weights
        state_dict = load_file(checkpoint_path)

        # Update model weights
        self.pipe.load_lora_weights(checkpoint_path)

    def generate_image(self, character):
        """
        Generates an image based on the character description.

        Args:
            character (dict): A dictionary containing character attributes.

        Returns:
            PIL.Image.Image: The generated image.
        """
        prompt = self.create_prompt(character)
        negative_prompt = self.create_negative_prompt()

        # Set a fixed seed for reproducibility (optional)
        generator = torch.Generator(device=self.device)
        generator.manual_seed(1)

        with torch.no_grad():
            if self.device.type in ['cuda']:
                with torch.autocast(self.device.type):
                    output = self.pipe(
                        prompt=prompt,
                        guidance_scale=5,
                        num_inference_steps=50,
                        height=512,
                        width=512,
                        negative_prompt=negative_prompt,
                        generator=generator,
                    )
            else:
                # For CPU, autocast is not used
                output = self.pipe(
                    prompt=prompt,
                    guidance_scale=5,
                    num_inference_steps=50,
                    height=512,
                    width=512,
                    negative_prompt=negative_prompt,
                    generator=generator,
                )

        image = output.images[0]
        return image

    def create_prompt(self, character_prompt):
        """
        Creates a text prompt based on the character attributes.

        Args:
            character_prompt (str): A string containing character attributes as a prompt.

        Returns:
            str: A text prompt.
        """

        # Filter out empty strings and join the attributes
        prompt = 'photo of ' + character_prompt

        prompt += " (cinematic lighting:1.1) dynamic angle, highest quality,  (movie poster pose), analog style, high-resolution, detailed, concept art"
        print(f"Prompt: {prompt}")

        return prompt
    
    def create_negative_prompt(self):
        """
        Creates a negative text prompt to improve image quality.

        Returns:
            str: A negative text prompt.
        """
        negative_prompt = "(nude), breasts, photoshop, airbrush, kitsch, oversaturated, low-res, Deformed, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limb,poorly drawn hands, missing limb, floating limbs, disconnected limbs, malformed hands, long neck, long body, disgusting, poorly drawn, mutilated, mangled, conjoined twins, extra legs, extra arms, meme, deformed, elongated, strabismus, heterochromia, watermark, extra fingers, blind eyes, dead eyes"
        print(f"Negative prompt: {negative_prompt}")
        return negative_prompt
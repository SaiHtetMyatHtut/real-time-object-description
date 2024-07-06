import os
import onnxruntime_genai as og

class Phi3Vision:
    def __init__(self, model_path):
        print("Loading model...")
        self.model = og.Model(model_path)
        self.processor = self.model.create_multimodal_processor()
        self.tokenizer_stream = self.processor.create_stream()

    def process_image(self, image_path, prompt_text):
        # Load and process image
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        image = og.Images.open(image_path)
        
        # Prepare prompt
        prompt = "<|user|>\n<|image_1|>\n"
        prompt += f"{prompt_text}<|end|>\n<|assistant|>\n"

        # Process input
        inputs = self.processor(prompt, images=image)

        # Generate response
        params = og.GeneratorParams(self.model)
        params.set_inputs(inputs)
        params.set_search_options(max_length=3072)

        generator = og.Generator(self.model, params)

        response = ""
        while not generator.is_done():
            generator.compute_logits()
            generator.generate_next_token()

            new_token = generator.get_next_tokens()[0]
            response += self.tokenizer_stream.decode(new_token)

        # Clean up
        del generator

        return response.strip()


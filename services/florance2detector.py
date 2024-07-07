import requests
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM

class Florance2Detector:
    def __init__(self):
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/Florence-2-large", trust_remote_code=True)
        self.processor = AutoProcessor.from_pretrained("microsoft/Florence-2-large", trust_remote_code=True)

    def detect_objects(self, image):
        prompt = "<DENSE_REGION_CAPTION>"

        inputs = self.processor(text=prompt, images=image, return_tensors="pt")

        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            num_beams=3,
            do_sample=False
        )
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

        parsed_answer = self.processor.post_process_generation(generated_text, task="<DENSE_REGION_CAPTION>", image_size=(image.width, image.height))

        return parsed_answer

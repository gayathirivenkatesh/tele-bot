from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Load the processor and BLIP model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def analyze_image_with_blip(image_path: str):
    """
    Analyzes an image using the BLIP model and generates a caption.

    :param image_path: Path to the image file.
    :return: Generated caption.
    """
    try:
        # Open the image using PIL
        image = Image.open(image_path).convert("RGB")

        # Process the image and generate caption
        inputs = processor(images=image, return_tensors="pt")
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)

        return f"📷 Generated Caption: {caption}"

    except Exception as e:
        return f"❌ Error analyzing image: {str(e)}"

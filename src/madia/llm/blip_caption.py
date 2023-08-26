from __future__ import annotations

import requests
import torch
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor


def caption_image_url(
    img_url,
    hf_model="Salesforce/blip-image-captioning-large",
    *,
    input_text="",
    return_tensors="pt",
    max_new_tokens=100,
    skip_special_tokens=True,
):
    # use GPU if it's available
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # preprocessor will prepare images for the model
    processor = BlipProcessor.from_pretrained(hf_model)
    # then we initialize the model itself
    model = BlipForConditionalGeneration.from_pretrained(hf_model).to(device)

    image = Image.open(requests.get(img_url, stream=True).raw).convert("RGB")

    # unconditional image captioning
    inputs = processor(image, input_text, return_tensors=return_tensors).to(device)

    out = model.generate(**inputs, max_new_tokens=max_new_tokens)

    return processor.decode(out[0], skip_special_tokens=skip_special_tokens)

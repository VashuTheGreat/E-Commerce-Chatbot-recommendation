import vconsoleprint
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("GOOGLE_GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# Read image


# Prompt for structured product extraction
prompt = """
You will be given an image. 
First, understand the image completely.

Then output ONLY a JSON object in this exact structure:

{
  "main_product": {
    "name": "",
    "color": "",
    "pattern": "",
    "type_style": "",
    "category_or_gender": ""
  },
  "additional_items": [
    {
      "name": "",
      "color": "",
      "pattern": "",
      "type_style": "",
      "category_or_gender": ""
    }
  ]
}

Rules:
- Detect only product-related information; ignore person details.
- "main_product" should be the most dominant/primary product (e.g., kurti, shirt, jeans, shoes).
- Include simple, clean color names (e.g., "light pink", "black").
- Pattern simple: floral, plain, striped, checkered.
- Type/style simple: halter-neck, round-neck, v-neck, slim-fit, etc.
- category_or_gender example: "women's apparel", "men's footwear", "accessory".
- "additional_items" must be a list of JSON objects with the SAME structure.
- If a field does not apply, leave it as "" (empty string).
- Return ONLY valid JSON, with no explanation.

Now analyze the image and return the JSON.
"""



def get_response(image_bytes):
    contents = [
        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
        prompt
    ]

    response = client.models.generate_content(model="gemini-2.5-flash", contents=contents)

    # print(response.text)

    text=response.text.strip()
    start = text.find("{")
    end = text.rfind("}") + 1

    json_str = text[start:end]

    data = json.loads(json_str)
    return data
   



if __name__=="__main__":
  with open("./shut.jpg", "rb") as f:
    image_bytes = f.read()

  r=get_response(image_bytes)
  print(r)   
  

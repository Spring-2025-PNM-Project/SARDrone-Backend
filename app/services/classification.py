import os
import json
import PIL.Image

from dotenv import load_dotenv
from google import genai
from io import BytesIO


load_dotenv()


GEMINI_MODEL = "gemini-2.0-flash"
PROMPT = '''
You are an AI vision model deployed on a Search and Rescue (SAR) drone.

Task:
Analyze the provided image and detect any humans.

Important Constraints:
Only detect humans.


Return output strictly in the JSON format provided. Do not add any extra commentary or text outside the JSON.
Bounding boxes must follow this exact format: [ymin, xmin, ymax, xmax] with integers between 0 and 1000.

JSON Response Format:
{
  "text_description": "Brief summary of the scene and any humans detected.",
  "confidence_score": integer from 1 to 100 indicating confidence a human is present,
  "bounding_boxes": [
    [ymin, xmin, ymax, xmax],
    ...
  ]
}

If no humans are detected, set confidence_score to 0 and leave bounding_boxes as an empty list.
'''

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class ClassificationModel:
    client = genai.Client(api_key=GEMINI_API_KEY)

    @staticmethod
    def generate(image_bytes: bytes):
        try:
            image = PIL.Image.open(BytesIO(image_bytes))

            response = ClassificationModel.client.models.generate_content(
                model = GEMINI_MODEL,
                contents = [image, PROMPT]
            ).text
            
            lines = response.splitlines()
            for i, line in enumerate(lines):
                if line == "```json":
                    response = "\n".join(lines[i+1:])
                    response = response.split("```")[0]
                    break
            
            return json.loads(response)
        except Exception as e:
            print("Gemini Error", e)

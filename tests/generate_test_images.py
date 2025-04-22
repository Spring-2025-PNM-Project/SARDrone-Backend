import time
import mimetypes
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import uuid



FOLDER_NAME = "images/no_human"
NUM_TO_GENERATE = 25
PROMPT = """Generate a drone view of a deserted natural area with a human being able to be seen, 
to test a SAR drone. """

PROMPT = """Generate a drone view of a deserted natural area with no human, to test a SAR drone. """


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


os.makedirs("images/yes_human", exist_ok=True)
os.makedirs("images/no_human", exist_ok=True)


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")


def generate():
    client = genai.Client(
        api_key=GEMINI_API_KEY,
    )

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=PROMPT),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "image",
            "text",
        ],
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if chunk.candidates[0].content.parts[0].inline_data:
            file_name = FOLDER_NAME + '/' + f"{uuid.uuid4().hex}.jpg"
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            save_binary_file(f"{file_name}{file_extension}", data_buffer)
        else:
            print(chunk.text)

if __name__ == "__main__":
    for i in range(NUM_TO_GENERATE):
        time.sleep(5)
        generate()

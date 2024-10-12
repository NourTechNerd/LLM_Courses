from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import HumanMessage,SystemMessage
from typing import List

class Extractor_Output(BaseModel):
    """Your description of the Image here."""
    Description : str = Field(..., description="This is your Description of the image")
    Items : str = Field(..., description="This is the python List of items in the image")


system_extractor = """You are a helpful image scraper.\n"""

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",api_key=GOOGLE_API_KEY)
structured_llm_extractor = llm.with_structured_output(Extractor_Output)


Image_URL = "https://upload.wikimedia.org/wikipedia/commons/3/32/Googleplex_HQ_%28cropped%29.jpg"

Help = "Google"
message = HumanMessage(
    content=[
        {
            "type": "text",
            "text": "What's in this image?",
        },  # You can optionally provide text parts
        {"type": "image_url", "image_url": {"url":Image_URL}},
    ]
)
Messages =   [
            SystemMessage(content=system_extractor),
            HumanMessage(
                content=[
                    {"type": "text",
                     "text": f"""
                        What's in this image?\n\n
                        help : {Help}\n\n
                        """
                    },
                    {"type": "image_url", "image_url": {"url": Image_URL}},
                ]
            )
        ]


response = structured_llm_extractor.invoke(Messages)
print(response.Items)
print(type(response.Items))
def string_to_list(input_string):
    # Remove the square brackets and split by commas, stripping any extra spaces
    return [item.strip() for item in input_string.strip("[]").split(",")]

# Example usage
input_string = response.Items
result_list = string_to_list(input_string)

print(result_list[0])  # Output: ['Building', 'Logo', 'Grass', 'Trees']
print(type(result_list))

from fastapi import Depends, FastAPI, Header, HTTPException
from langchain_core.runnables import RunnableLambda
from typing_extensions import Annotated
from langchain.pydantic_v1 import Field
from langserve import add_routes


"""async def verify_token(x_token: Annotated[str, Header()]) -> None:
    # Replace this with your actual authentication logic
    if x_token != "1111":
        raise HTTPException(status_code=400, detail="X-Token header invalid")
"""

app = FastAPI(
    title="LangChain Server",
    version="1.0",
)

#################### ROUTE1

def add_one(x: int) -> int:
    """Add one to an integer."""
    return x + 1
chain = RunnableLambda(add_one)
add_routes(
    app,
    chain,
    path="/chain"
)

#################### ROUTE2

from langserve import CustomUserType
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_core.messages import HumanMessage

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

vlm = ChatGoogleGenerativeAI(model="gemini-1.5-flash",api_key=GOOGLE_API_KEY,temperature=0.2)


class VLM_Input(CustomUserType):
    text: str
    Image_URL : str
 
class VLM_Output(CustomUserType):
    Items: str 
    Description: str
 
# To use the Stream mode with LLMs we need a asynch function with yield intsead of return.   
async def Run_VLM(Input: VLM_Input):
    text = Input.text
    image_url = Input.Image_URL
    prompt = [ 
        HumanMessage(
            content=[
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        )
    ]
    async for chunk in vlm.astream(prompt):
        output = VLM_Output(Items=chunk.name,Description=chunk.content)
        yield text

def Run_VLM11(Input : VLM_Input):
    text = Input.text
    image_url = Input.Image_URL
    prompt = [ 
        HumanMessage(
            content=[
                {"type": "text", "text": text},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        )
    ]
    response = vlm.invoke(prompt)
    return VLM_Output(Items="1",Description=response.content)

add_routes(
    app,
    RunnableLambda(Run_VLM11),
    path="/Flash",
)

add_routes(
    app,
    RunnableLambda(Run_VLM),
    path="/Flash_Async",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)